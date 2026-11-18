from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSpinBox, QVBoxLayout, QWidget,
)

from ui.config_card.ajustes import (
    ALTO_BASE_PX, ANCHO_BASE_PX, ALTO_CR80_MM, ANCHO_CR80_MM,
    leer_int, leer_str,
)
from ui.config_card.widgets_comunes import ruta_relativa


class TabGeneral(QWidget):
    # ancho, alto finales del lienzo de diseño (px de la imagen base)
    dimensionesCambiadas = Signal(float, float)
    carpetaCambiada = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Plantilla ---
        gb_plantilla = QGroupBox("Plantilla")
        f1 = QFormLayout(gb_plantilla)
        self.ed_carpeta = QLineEdit()
        self.ed_carpeta.setReadOnly(True)
        btn = QPushButton("Examinar...")
        btn.clicked.connect(self._elegir_carpeta)
        fila = QHBoxLayout()
        fila.addWidget(self.ed_carpeta)
        fila.addWidget(btn)
        f1.addRow("Carpeta:", fila)
        self.ed_fondo_frontal = QLineEdit("fondo_frontal.png")
        self.ed_fondo_trasero = QLineEdit("fondo_trasero.png")
        f1.addRow("Fondo frontal:", self.ed_fondo_frontal)
        f1.addRow("Fondo trasero:", self.ed_fondo_trasero)

        # --- Formato / impresión ---
        gb_formato = QGroupBox("Formato e impresión")
        f2 = QFormLayout(gb_formato)
        self.cb_orientacion = QComboBox()
        self.cb_orientacion.addItem("Horizontal", "horizontal")
        self.cb_orientacion.addItem("Vertical", "vertical")
        self.sp_dpi = QSpinBox()
        self.sp_dpi.setRange(96, 1200)
        self.sp_dpi.setSingleStep(50)
        self.sp_dpi.setValue(300)
        self.sp_dpi.setSuffix(" dpi")
        self.lbl_lienzo = QLabel()
        self.lbl_impresion = QLabel()

        f2.addRow("Orientación:", self.cb_orientacion)
        f2.addRow("Resolución de impresión:", self.sp_dpi)
        f2.addRow("Tamaño de la imagen base:", self.lbl_lienzo)
        f2.addRow("Tamaño de impresión (CR80):", self.lbl_impresion)

        lay = QVBoxLayout(self)
        lay.addWidget(gb_plantilla)
        lay.addWidget(gb_formato)
        lay.addStretch()

        self.cb_orientacion.currentIndexChanged.connect(self._actualizar)
        self.sp_dpi.valueChanged.connect(self._actualizar)
        self._actualizar()

    def dimensiones(self):
        """Tamaño del lienzo de diseño en px de la imagen base (según orientación)."""
        if self.cb_orientacion.currentData() == "horizontal":
            return ANCHO_BASE_PX, ALTO_BASE_PX
        return ALTO_BASE_PX, ANCHO_BASE_PX

    def _actualizar(self):
        ancho, alto = self.dimensiones()
        self.lbl_lienzo.setText(f"{ancho} × {alto} px")
        if self.cb_orientacion.currentData() == "horizontal":
            self.lbl_impresion.setText(f"{ANCHO_CR80_MM} × {ALTO_CR80_MM} mm")
        else:
            self.lbl_impresion.setText(f"{ALTO_CR80_MM} × {ANCHO_CR80_MM} mm")
        self.dimensionesCambiadas.emit(ancho, alto)

    def _elegir_carpeta(self):
        c = QFileDialog.getExistingDirectory(
            self, "Carpeta de plantilla", self.ed_carpeta.text()
        )
        if c:
            self.ed_carpeta.setText(c)
            self.carpetaCambiada.emit(c)

    def cargar(self, s):
        self.ed_carpeta.setText(leer_str(s, "general/carpeta_plantilla"))
        self.ed_fondo_frontal.setText(leer_str(s, "general/fondo_frontal", "fondo_frontal.png"))
        self.ed_fondo_trasero.setText(leer_str(s, "general/fondo_trasero", "fondo_trasero.png"))
        self.cb_orientacion.blockSignals(True)
        self.cb_orientacion.setCurrentIndex(
            max(self.cb_orientacion.findData(leer_str(s, "general/orientacion", "horizontal")), 0))
        self.cb_orientacion.blockSignals(False)
        self.sp_dpi.setValue(leer_int(s, "general/dpi_impresion", 300))
        self._actualizar()
        self.carpetaCambiada.emit(self.ed_carpeta.text())

    def guardar(self, s):
        ancho, alto = self.dimensiones()
        s.setValue("general/carpeta_plantilla", self.ed_carpeta.text())
        s.setValue("general/fondo_frontal", self.ed_fondo_frontal.text().strip())
        s.setValue("general/fondo_trasero", self.ed_fondo_trasero.text().strip())
        s.setValue("general/orientacion", self.cb_orientacion.currentData())
        s.setValue("general/ancho_px", ancho)
        s.setValue("general/alto_px", alto)
        s.setValue("general/dpi_impresion", self.sp_dpi.value())

    def restablecer(self):
        self.ed_fondo_frontal.setText("fondo_frontal.png")
        self.ed_fondo_trasero.setText("fondo_trasero.png")
        self.cb_orientacion.setCurrentIndex(0)
        self.sp_dpi.setValue(300)
        self._actualizar()
