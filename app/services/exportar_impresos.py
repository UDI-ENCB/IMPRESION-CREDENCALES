from openpyxl import Workbook
from openpyxl.styles import Font
from pathlib import Path

COLUMNAS = (
    ("Boleta", "numero_usuario"),
    ("Nombre completo", "nombre_completo"),
    ("Area", "area"),
)


def registros_impresos(datos: list[dict]) -> list[dict]:
    """Devuelve los registros que ya tienen fecha de impresion."""
    return [registro for registro in datos if registro.get("fecha_impresion")]


def exportar_impresos(datos: list[dict], ruta: str | Path) -> int:
    """Escribe en un xlsx los registros impresos y devuelve cuantos exporto."""
    impresos = registros_impresos(datos)

    wb = Workbook()
    hoja = wb.active
    hoja.title = "Impresos"

    hoja.append([titulo for titulo, _ in COLUMNAS])
    for celda in hoja[1]:
        celda.font = Font(bold=True)

    for registro in impresos:
        hoja.append([registro.get(campo) for _, campo in COLUMNAS])

    for indice, (titulo, _) in enumerate(COLUMNAS, start=1):
        letra = hoja.cell(row=1, column=indice).column_letter
        hoja.column_dimensions[letra].width = max(len(titulo) + 4, 18)

    hoja.freeze_panes = "A2"
    wb.save(Path(ruta))
    return len(impresos)
