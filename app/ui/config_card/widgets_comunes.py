import os

from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QCheckBox, QColorDialog, QComboBox, QDoubleSpinBox, QFileDialog,
    QFontComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QScrollArea, QSpinBox, QVBoxLayout, QWidget,
)

from ui.config_card.ajustes import leer_bool, leer_float, leer_int, leer_str


def ruta_relativa(ruta: str, carpeta: str) -> str:
    """Devuelve la ruta relativa a la carpeta de plantilla si está dentro de ella."""
    if not carpeta:
        return ruta
    try:
        rel = os.path.relpath(ruta, carpeta)
    except ValueError:  # unidades distintas en Windows
        return ruta
    return ruta if rel.startswith("..") else rel.replace("\\", "/")


class ColorButton(QPushButton):
    def __init__(self, color="#000000", parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self.setFixedWidth(70)
        self.clicked.connect(self._elegir)
        self._pintar()

    def _pintar(self):
        self.setStyleSheet(
            f"background-color: {self._color.name()}; border: 1px solid #555;"
        )
        self.setToolTip(self._color.name())

    def _elegir(self):
        c = QColorDialog.getColor(self._color, self, "Seleccionar color")
        if c.isValid():
            self._color = c
            self._pintar()

    def color(self) -> str:
        return self._color.name()

    def set_color(self, color: str):
        self._color = QColor(color)
        self._pintar()


def _fila(*widgets) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    for x in widgets:
        lay.addWidget(QLabel(x) if isinstance(x, str) else x)
    lay.addStretch()
    return w


class ElementoBase(QGroupBox):
    """Elemento con posición (x, y) y tamaño máximo (ancho, alto) en píxeles."""

    def __init__(self, titulo, prefijo, geom, parent=None):
        super().__init__(titulo, parent)
        self.prefijo = prefijo
        self.geom_defecto = geom  # (x, y, w, h)
        self.form = QFormLayout(self)

        self.sp_x, self.sp_y, self.sp_w, self.sp_h = (self._spin() for _ in range(4))
        self.form.addRow("Posición:", _fila("X", self.sp_x, "Y", self.sp_y))
        self.form.addRow("Tamaño máx.:", _fila("Ancho", self.sp_w, "Alto", self.sp_h))
        self._poner_geom(geom)

    @staticmethod
    def _spin():
        sp = QDoubleSpinBox()
        sp.setRange(0, 3000)
        sp.setDecimals(0)
        sp.setSingleStep(5)
        sp.setSuffix(" px")
        return sp

    def _poner_geom(self, g):
        for sp, v in zip((self.sp_x, self.sp_y, self.sp_w, self.sp_h), g):
            sp.setValue(v)

    def set_limites(self, ancho: float, alto: float):
        self.sp_x.setMaximum(ancho)
        self.sp_w.setMaximum(ancho)
        self.sp_y.setMaximum(alto)
        self.sp_h.setMaximum(alto)

    def cargar(self, s):
        p = self.prefijo
        for sp, k, d in zip(
            (self.sp_x, self.sp_y, self.sp_w, self.sp_h),
            ("x", "y", "w", "h"),
            self.geom_defecto,
        ):
            sp.setValue(leer_float(s, f"{p}/{k}", d))

    def guardar(self, s):
        p = self.prefijo
        s.setValue(f"{p}/x", self.sp_x.value())
        s.setValue(f"{p}/y", self.sp_y.value())
        s.setValue(f"{p}/w", self.sp_w.value())
        s.setValue(f"{p}/h", self.sp_h.value())

    def restablecer(self):
        self._poner_geom(self.geom_defecto)


class ElementoImagen(ElementoBase):
    """Imagen/QR/máscara. Si archivo es None no muestra selector de archivo."""

    def __init__(self, titulo, prefijo, geom, archivo=None, parent=None):
        super().__init__(titulo, prefijo, geom, parent)
        self.archivo_defecto = archivo
        self.carpeta = ""
        self.ed_archivo = None
        if archivo is not None:
            self.ed_archivo = QLineEdit(archivo)
            btn = QPushButton("...")
            btn.setFixedWidth(30)
            btn.clicked.connect(self._examinar)
            self.form.insertRow(0, "Archivo:", _fila(self.ed_archivo, btn))

    def set_carpeta(self, carpeta: str):
        self.carpeta = carpeta

    def _examinar(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", self.carpeta,
            "Imágenes (*.png *.jpg *.jpeg *.bmp)",
        )
        if ruta:
            self.ed_archivo.setText(ruta_relativa(ruta, self.carpeta))

    def cargar(self, s):
        super().cargar(s)
        if self.ed_archivo:
            self.ed_archivo.setText(
                leer_str(s, f"{self.prefijo}/archivo", self.archivo_defecto)
            )

    def guardar(self, s):
        super().guardar(s)
        if self.ed_archivo:
            s.setValue(f"{self.prefijo}/archivo", self.ed_archivo.text().strip())

    def restablecer(self):
        super().restablecer()
        if self.ed_archivo:
            self.ed_archivo.setText(self.archivo_defecto)


class ElementoTexto(ElementoBase):
    """Texto con fuente, tamaño, color, estilo y alineación individuales.
    texto=None -> el contenido es dinámico (dato del usuario) y no se edita."""

    ALINEACIONES = [("Izquierda", "izquierda"), ("Centro", "centro"), ("Derecha", "derecha")]

    def __init__(self, titulo, prefijo, geom, texto=None, multilinea=False,
                 fuente="Arial", tam=10, color="#000000", negrita=False,
                 cursiva=False, alineacion="izquierda", parent=None):
        super().__init__(titulo, prefijo, geom, parent)
        self.d = dict(texto=texto, fuente=fuente, tam=tam, color=color,
                      negrita=negrita, cursiva=cursiva, alineacion=alineacion)
        self.multilinea = multilinea

        self.ed_texto = None
        if texto is not None:
            if multilinea:
                self.ed_texto = QPlainTextEdit()
                self.ed_texto.setFixedHeight(60)
            else:
                self.ed_texto = QLineEdit()
            self.form.insertRow(0, "Texto:", self.ed_texto)

        self.cb_fuente = QFontComboBox()
        self.sp_tam = QSpinBox()
        self.sp_tam.setRange(4, 72)
        self.sp_tam.setSuffix(" pt")
        self.chk_negrita = QCheckBox("Negrita")
        self.chk_cursiva = QCheckBox("Cursiva")
        self.btn_color = ColorButton()
        self.cb_alin = QComboBox()
        for nombre, valor in self.ALINEACIONES:
            self.cb_alin.addItem(nombre, valor)

        self.form.addRow("Fuente:", _fila(self.cb_fuente, self.sp_tam))
        self.form.addRow("Estilo:", _fila(self.chk_negrita, self.chk_cursiva))
        self.form.addRow("Color / Alineación:", _fila(self.btn_color, self.cb_alin))
        self._poner_estilo(self.d)

    def _get_texto(self):
        return (self.ed_texto.toPlainText() if self.multilinea
                else self.ed_texto.text())

    def _set_texto(self, t):
        if self.ed_texto is None:
            return
        (self.ed_texto.setPlainText if self.multilinea else self.ed_texto.setText)(t)

    def _poner_estilo(self, d):
        self._set_texto(d["texto"] or "")
        self.cb_fuente.setCurrentFont(QFont(d["fuente"]))
        self.sp_tam.setValue(d["tam"])
        self.chk_negrita.setChecked(d["negrita"])
        self.chk_cursiva.setChecked(d["cursiva"])
        self.btn_color.set_color(d["color"])
        i = self.cb_alin.findData(d["alineacion"])
        self.cb_alin.setCurrentIndex(max(i, 0))

    def cargar(self, s):
        super().cargar(s)
        p, d = self.prefijo, self.d
        self._poner_estilo(dict(
            texto=leer_str(s, f"{p}/texto", d["texto"] or ""),
            fuente=leer_str(s, f"{p}/fuente", d["fuente"]),
            tam=leer_int(s, f"{p}/tam", d["tam"]),
            color=leer_str(s, f"{p}/color", d["color"]),
            negrita=leer_bool(s, f"{p}/negrita", d["negrita"]),
            cursiva=leer_bool(s, f"{p}/cursiva", d["cursiva"]),
            alineacion=leer_str(s, f"{p}/alineacion", d["alineacion"]),
        ))

    def guardar(self, s):
        super().guardar(s)
        p = self.prefijo
        if self.ed_texto is not None:
            s.setValue(f"{p}/texto", self._get_texto())
        s.setValue(f"{p}/fuente", self.cb_fuente.currentFont().family())
        s.setValue(f"{p}/tam", self.sp_tam.value())
        s.setValue(f"{p}/negrita", self.chk_negrita.isChecked())
        s.setValue(f"{p}/cursiva", self.chk_cursiva.isChecked())
        s.setValue(f"{p}/color", self.btn_color.color())
        s.setValue(f"{p}/alineacion", self.cb_alin.currentData())

    def restablecer(self):
        super().restablecer()
        self._poner_estilo(self.d)


class TabBase(QWidget):
    """Pestaña con scroll que contiene una lista de elementos configurables."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.elementos = []
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        raiz.addWidget(scroll)
        contenedor = QWidget()
        self._lay = QVBoxLayout(contenedor)
        scroll.setWidget(contenedor)

    def agregar(self, elemento):
        self.elementos.append(elemento)
        self._lay.addWidget(elemento)

    def finalizar(self):
        self._lay.addStretch()

    def set_dimensiones(self, ancho: float, alto: float):
        """Establece los límites de los elementos en píxeles (ancho/alto de la tarjeta)."""
        for e in self.elementos:
            e.set_limites(ancho, alto)

    def set_carpeta(self, carpeta: str):
        for e in self.elementos:
            if hasattr(e, "set_carpeta"):
                e.set_carpeta(carpeta)

    def cargar(self, s):
        for e in self.elementos:
            e.cargar(s)

    def guardar(self, s):
        for e in self.elementos:
            e.guardar(s)

    def restablecer(self):
        for e in self.elementos:
            e.restablecer()