from PySide6.QtCore import QSettings

ORGANIZACION = "ENCB"
APLICACION = "ConfiguracionCredencial"

INCH_MM = 25.4              # milímetros por pulgada

# --- Imagen base de la credencial (espacio de trabajo en píxeles) ---
# La plantilla PNG tiene esta resolución; sobre ella se diseña el layout.
ANCHO_BASE_PX = 1063       # píxeles de ancho de la imagen base
ALTO_BASE_PX = 697         # píxeles de alto de la imagen base

# --- Tarjeta CR80 (tamaño físico de impresión, en milímetros) ---
ANCHO_CR80_MM = 85.6
ALTO_CR80_MM = 54.0
# Factor de escala de la imagen base al tamaño físico CR80
ESCALA_BASE_A_CR80 = ANCHO_CR80_MM / ANCHO_BASE_PX


def mm_a_px(mm_val: float, dpi: float) -> float:
    """Convierte milímetros a píxeles según la resolución indicada."""
    return mm_val * dpi / INCH_MM


def px_a_mm(px: float, dpi: float) -> float:
    """Convierte píxeles a milímetros según la resolución indicada."""
    return px * INCH_MM / dpi


def obtener_ajustes() -> QSettings:
    return QSettings(ORGANIZACION, APLICACION)


def leer_float(s: QSettings, clave: str, defecto: float) -> float:
    try:
        return float(s.value(clave, defecto))
    except (TypeError, ValueError):
        return float(defecto)


def leer_int(s: QSettings, clave: str, defecto: int) -> int:
    try:
        return int(s.value(clave, defecto))
    except (TypeError, ValueError):
        return int(defecto)


def leer_bool(s: QSettings, clave: str, defecto: bool) -> bool:
    v = s.value(clave, defecto)
    if isinstance(v, bool):
        return v
    return str(v).lower() == "true"


def leer_str(s: QSettings, clave: str, defecto: str = "") -> str:
    v = s.value(clave, defecto)
    return defecto if v is None else str(v)