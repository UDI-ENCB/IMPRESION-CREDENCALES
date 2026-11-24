from pathlib import Path
from os.path import join

FILTROS_DEFAULT = {
    "activos": True,
    "impresion": "todos",
    "foto": "todos",
    "remplazo": "todos",
    "solo_encontrados": True,
}


def _tiene_fecha(registro: dict) -> bool:
    return bool(registro.get("fecha_impresion"))


def _tiene_remplazo(registro: dict, directorio: str | None) -> bool:
    numero_usuario = registro.get("numero_usuario")
    if not directorio or not numero_usuario:
        return False
    archivo = Path(join(directorio, f"{numero_usuario}.jpg"))
    return archivo.exists() and archivo.is_file()


def actualizar_remplazo(registro: dict, directorio: str | None) -> bool:
    """Recalcula remplazo_foto contra el directorio y lo deja en el registro."""
    registro["remplazo_foto"] = _tiene_remplazo(registro, directorio)
    return registro["remplazo_foto"]


def cumple(registro: dict, filtros: dict, directorio: str | None) -> bool:
    if filtros.get("solo_encontrados", True) and not registro.get("encontrado", False):
        return False

    impresion = filtros.get("impresion", "todos")
    if impresion == "impresos" and not _tiene_fecha(registro):
        return False
    if impresion == "sin_imprimir" and _tiene_fecha(registro):
        return False

    foto = filtros.get("foto", "todos")
    if foto == "con" and not registro.get("fotografia", False):
        return False
    if foto == "sin" and registro.get("fotografia", False):
        return False

    remplazo = filtros.get("remplazo", "todos")
    if remplazo != "todos":
        tiene = actualizar_remplazo(registro, directorio)
        if remplazo == "con" and not tiene:
            return False
        if remplazo == "sin" and tiene:
            return False

    return True


def filtrar(datos: list[dict], filtros: dict | None = None,
            directorio: str | None = None) -> list[dict]:
    """Devuelve los registros que cumplen los filtros activos."""
    filtros = filtros or FILTROS_DEFAULT
    if not filtros.get("activos", True):
        return list(datos)
    return [registro for registro in datos if cumple(registro, filtros, directorio)]


def indice_por_usuario(datos: list[dict], numero_usuario) -> int:
    """Busca por numero de usuario para no depender del indice de la tabla."""
    buscado = str(numero_usuario).strip().upper()
    for indice, registro in enumerate(datos):
        if str(registro.get("numero_usuario", "")).strip().upper() == buscado:
            return indice
    return -1


def actualizar_registro(datos: list[dict], registro: dict) -> bool:
    indice = indice_por_usuario(datos, registro.get("numero_usuario"))
    if indice < 0:
        return False
    datos[indice] = registro
    return True


def eliminar_registro(datos: list[dict], numero_usuario) -> bool:
    indice = indice_por_usuario(datos, numero_usuario)
    if indice < 0:
        return False
    del datos[indice]
    return True
