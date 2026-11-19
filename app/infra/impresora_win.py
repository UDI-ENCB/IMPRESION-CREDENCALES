"""Consulta de estado y cola de impresion en Windows mediante ctypes.

No requiere pywin32: usa winspool.drv, disponible en la stdlib.
"""

from __future__ import annotations

import asyncio
import ctypes
import time
from ctypes import wintypes
from dataclasses import dataclass
from typing import Callable

PRINTER_ACCESS_USE = 0x00000008

ESTADOS_IMPRESORA = {
    0x00000001: "en pausa",
    0x00000002: "error",
    0x00000008: "atasco de papel",
    0x00000010: "sin papel",
    0x00000040: "problema de papel",
    0x00000080: "sin conexion",
    0x00001000: "no disponible",
    0x00020000: "toner bajo",
    0x00040000: "sin toner",
    0x00080000: "pagina expulsada",
    0x00100000: "requiere intervencion del usuario",
    0x00200000: "sin memoria",
    0x00400000: "puerta abierta",
}

ATRIBUTOS_IMPRESORA = {
    0x00000100: "trabajando sin conexion",
}

ESTADOS_TRABAJO_ERROR = {
    0x00000002: "error",
    0x00000020: "sin conexion",
    0x00000040: "sin papel",
    0x00000200: "cola bloqueada",
    0x00000400: "requiere intervencion del usuario",
}

ESTADOS_TRABAJO_FIN = {
    0x00000080: "impreso",
    0x00001000: "completado",
}

ESTADOS_TRABAJO_INFO = {
    0x00000001: "en pausa",
    0x00000004: "eliminando",
    0x00000008: "en cola",
    0x00000010: "imprimiendo",
    0x00000100: "eliminado",
    0x00000800: "reiniciando",
    0x00002000: "retenido",
}


@dataclass
class Resultado:
    ok: bool
    cancelado: bool = False
    mensaje: str = ""


class PRINTER_DEFAULTSW(ctypes.Structure):
    _fields_ = [
        ("pDatatype", wintypes.LPWSTR),
        ("pDevMode", ctypes.c_void_p),
        ("DesiredAccess", wintypes.DWORD),
    ]


class PRINTER_INFO_2W(ctypes.Structure):
    _fields_ = [
        ("pServerName", wintypes.LPWSTR),
        ("pPrinterName", wintypes.LPWSTR),
        ("pShareName", wintypes.LPWSTR),
        ("pPortName", wintypes.LPWSTR),
        ("pDriverName", wintypes.LPWSTR),
        ("pComment", wintypes.LPWSTR),
        ("pLocation", wintypes.LPWSTR),
        ("pDevMode", ctypes.c_void_p),
        ("pSepFile", wintypes.LPWSTR),
        ("pPrintProcessor", wintypes.LPWSTR),
        ("pDatatype", wintypes.LPWSTR),
        ("pParameters", wintypes.LPWSTR),
        ("pSecurityDescriptor", ctypes.c_void_p),
        ("Attributes", wintypes.DWORD),
        ("Priority", wintypes.DWORD),
        ("DefaultPriority", wintypes.DWORD),
        ("StartTime", wintypes.DWORD),
        ("UntilTime", wintypes.DWORD),
        ("Status", wintypes.DWORD),
        ("cJobs", wintypes.DWORD),
        ("AveragePPM", wintypes.DWORD),
    ]


class JOB_INFO_1W(ctypes.Structure):
    _fields_ = [
        ("JobId", wintypes.DWORD),
        ("pPrinterName", wintypes.LPWSTR),
        ("pMachineName", wintypes.LPWSTR),
        ("pUserName", wintypes.LPWSTR),
        ("pDocument", wintypes.LPWSTR),
        ("pDatatype", wintypes.LPWSTR),
        ("pStatus", wintypes.LPWSTR),
        ("Status", wintypes.DWORD),
        ("Priority", wintypes.DWORD),
        ("Position", wintypes.DWORD),
        ("TotalPages", wintypes.DWORD),
        ("PagesPrinted", wintypes.DWORD),
    ]


_winspool = ctypes.WinDLL("winspool.drv", use_last_error=True)

_winspool.OpenPrinterW.argtypes = [
    wintypes.LPWSTR,
    ctypes.POINTER(wintypes.HANDLE),
    ctypes.POINTER(PRINTER_DEFAULTSW),
]
_winspool.OpenPrinterW.restype = wintypes.BOOL
_winspool.ClosePrinter.argtypes = [wintypes.HANDLE]
_winspool.ClosePrinter.restype = wintypes.BOOL
_winspool.GetPrinterW.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
]
_winspool.GetPrinterW.restype = wintypes.BOOL
_winspool.EnumJobsW.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    ctypes.POINTER(wintypes.DWORD),
]
_winspool.EnumJobsW.restype = wintypes.BOOL


def _abrir(nombre: str) -> wintypes.HANDLE:
    handle = wintypes.HANDLE()
    defaults = PRINTER_DEFAULTSW(None, None, PRINTER_ACCESS_USE)
    if not _winspool.OpenPrinterW(nombre, ctypes.byref(handle), ctypes.byref(defaults)):
        error = ctypes.get_last_error()
        raise OSError(error, f"No se pudo abrir la impresora {nombre!r} (error {error})")
    return handle


def _leer_info2(handle: wintypes.HANDLE) -> dict:
    necesario = wintypes.DWORD(0)
    _winspool.GetPrinterW(handle, 2, None, 0, ctypes.byref(necesario))
    if necesario.value == 0:
        error = ctypes.get_last_error()
        raise OSError(error, f"GetPrinter no devolvio tamano (error {error})")
    buffer = ctypes.create_string_buffer(necesario.value)
    if not _winspool.GetPrinterW(
        handle, 2, ctypes.cast(buffer, ctypes.c_void_p), necesario.value, ctypes.byref(necesario)
    ):
        error = ctypes.get_last_error()
        raise OSError(error, f"GetPrinter fallo (error {error})")
    info = ctypes.cast(buffer, ctypes.POINTER(PRINTER_INFO_2W)).contents
    return {
        "status": info.Status,
        "attributes": info.Attributes,
        "trabajos": info.cJobs,
        "puerto": info.pPortName,
        "driver": info.pDriverName,
    }


def _nombres(bits: int, tabla: dict[int, str]) -> list[str]:
    return [texto for bit, texto in tabla.items() if bits & bit]


def estado_impresora(nombre: str) -> Resultado:
    """Comprueba el estado publicado por el driver antes de imprimir."""
    try:
        handle = _abrir(nombre)
    except OSError as exc:
        return Resultado(False, False, str(exc))
    try:
        info = _leer_info2(handle)
    except OSError as exc:
        return Resultado(False, False, str(exc))
    finally:
        _winspool.ClosePrinter(handle)

    problemas = _nombres(info["status"], ESTADOS_IMPRESORA)
    problemas += _nombres(info["attributes"], ATRIBUTOS_IMPRESORA)
    if problemas:
        return Resultado(
            False,
            False,
            f"La impresora {nombre!r} reporta: {', '.join(problemas)}",
        )
    return Resultado(True, False, "")


def trabajos_en_cola(nombre: str) -> list[dict]:
    """Trabajos pendientes en la cola local de esa impresora."""
    handle = _abrir(nombre)
    try:
        necesario = wintypes.DWORD(0)
        devueltos = wintypes.DWORD(0)
        _winspool.EnumJobsW(
            handle, 0, 99, 1, None, 0, ctypes.byref(necesario), ctypes.byref(devueltos)
        )
        if necesario.value == 0:
            return []
        buffer = ctypes.create_string_buffer(necesario.value)
        if not _winspool.EnumJobsW(
            handle,
            0,
            99,
            1,
            ctypes.cast(buffer, ctypes.c_void_p),
            necesario.value,
            ctypes.byref(necesario),
            ctypes.byref(devueltos),
        ):
            error = ctypes.get_last_error()
            raise OSError(error, f"EnumJobs fallo (error {error})")
        arreglo = ctypes.cast(buffer, ctypes.POINTER(JOB_INFO_1W))
        trabajos = []
        for posicion in range(devueltos.value):
            trabajo = arreglo[posicion]
            trabajos.append(
                {
                    "id": trabajo.JobId,
                    "status": trabajo.Status,
                    "flags": _nombres(
                        trabajo.Status,
                        {**ESTADOS_TRABAJO_INFO, **ESTADOS_TRABAJO_ERROR, **ESTADOS_TRABAJO_FIN},
                    ),
                    "paginas": trabajo.PagesPrinted,
                    "total": trabajo.TotalPages,
                    "documento": trabajo.pDocument,
                }
            )
        return trabajos
    finally:
        _winspool.ClosePrinter(handle)


def ids_en_cola(nombre: str) -> set[int]:
    """Ids de los trabajos ya presentes, para identificar el propio despues."""
    return {trabajo["id"] for trabajo in trabajos_en_cola(nombre)}


async def esperar_trabajo(
    nombre: str,
    ids_previos: set[int],
    timeout_s: float = 180.0,
    intervalo_s: float = 0.25,
    gracia_s: float = 1.5,
    sin_progreso_s: float = 120.0,
    cancelar: Callable[[], bool] | None = None,
) -> Resultado:
    """Espera a que el trabajo enviado salga de la cola o reporte error.

    La impresora mantiene el trabajo en la cola, con estado "imprimiendo",
    mientras dura la impresion, y lo retira al terminar: esa salida es el fin
    real. Por eso ``timeout_s`` es solo un tope de seguridad y el fallo por
    trabajo atascado lo detecta ``sin_progreso_s``, que vigila los cambios de
    estado y el avance de paginas impresas.
    """
    inicio = time.monotonic()
    ultimo_progreso = inicio
    job_id: int | None = None
    firma_previa: tuple[int, int] | None = None

    while True:
        if cancelar is not None and cancelar():
            return Resultado(False, True, "Impresion cancelada por el usuario")

        try:
            trabajos = trabajos_en_cola(nombre)
        except OSError as exc:
            return Resultado(False, False, str(exc))

        nuevos = [trabajo for trabajo in trabajos if trabajo["id"] not in ids_previos]
        if nuevos:
            trabajo = nuevos[0]
            job_id = trabajo["id"]
            if trabajo["status"] & sum(ESTADOS_TRABAJO_ERROR):
                return Resultado(
                    False,
                    False,
                    f"El trabajo {job_id} reporta: {', '.join(trabajo['flags'])}",
                )
            if trabajo["status"] & sum(ESTADOS_TRABAJO_FIN):
                return Resultado(True, False, "")
            firma = (trabajo["status"], trabajo["paginas"])
            if firma != firma_previa:
                firma_previa = firma
                ultimo_progreso = time.monotonic()
        elif job_id is not None:
            return Resultado(True, False, "")
        elif time.monotonic() - inicio >= gracia_s:
            return Resultado(True, False, "")

        ahora = time.monotonic()
        if ahora - ultimo_progreso >= sin_progreso_s:
            return Resultado(
                False,
                False,
                f"El trabajo {job_id} no avanzo en {sin_progreso_s:g}s",
            )
        if ahora - inicio >= timeout_s:
            if job_id is None:
                return Resultado(
                    False,
                    False,
                    f"El trabajo no aparecio en la cola en {timeout_s:g}s",
                )
            return Resultado(
                False,
                False,
                f"El trabajo {job_id} no termino en {timeout_s:g}s",
            )

        await asyncio.sleep(intervalo_s)
