from PySide6.QtWidgets import QComboBox, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QGroupBox, QSizePolicy, QLabel
from PySide6.QtGui import QPageSize
from qasync import asyncSlot
from core.app_state import AppState
from ui.global_status_bar import GlobalState


class PrinterPanel(QWidget):

    def __init__(self):
        super().__init__()
        self.estado = AppState()
        self.statusBar = GlobalState.obtener()

        self.combo_impresoras = QComboBox()
        self.combo_impresoras.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.combo_impresoras.currentTextChanged.connect(self.on_impresora_cambiada)

        self.button_refrescar = QPushButton("Actualizar")
        self.button_refrescar.clicked.connect(self.refrescar_impresoras)

        self.combo_tamanos = QComboBox()
        self.combo_tamanos.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.combo_tamanos.currentIndexChanged.connect(self.on_tamano_cambiado)

        layout_impresora = QHBoxLayout()
        layout_impresora.addWidget(self.combo_impresoras)
        layout_impresora.addWidget(self.button_refrescar)

        layout_tamanos = QHBoxLayout()
        layout_tamanos.addWidget(QLabel("Tamaño de impresión"))
        layout_tamanos.addWidget(self.combo_tamanos)

        layout = QVBoxLayout()
        layout.addLayout(layout_impresora)
        layout.addLayout(layout_tamanos)

        group_box = QGroupBox("Impresora")
        group_box.setLayout(layout)

        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(group_box)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.refrescar_impresoras()

    def refrescar_impresoras(self):
        disponibles = self.estado.impresoras_disponibles()
        seleccionada = self.estado.verificar_impresora()

        self.combo_impresoras.blockSignals(True)
        self.combo_impresoras.clear()
        self.combo_impresoras.addItems(disponibles)
        if seleccionada is not None:
            indice = self.combo_impresoras.findText(seleccionada)
            if indice >= 0:
                self.combo_impresoras.setCurrentIndex(indice)
        self.combo_impresoras.blockSignals(False)

        self.combo_impresoras.setEnabled(len(disponibles) > 0)

        if len(disponibles) == 0:
            self.statusBar.mostrar_aviso("No se encontraron impresoras instaladas")

        self.refrescar_tamanos()

    def refrescar_tamanos(self):
        tamanos = self.estado.tamanos_disponibles(self.estado.impresora)
        seleccionado = self.estado.verificar_tamano_pagina()
        self.combo_tamanos.blockSignals(True)
        self.combo_tamanos.clear()
        for tamano in tamanos:
            medidas = tamano.size(QPageSize.Unit.Millimeter)
            texto = f"{tamano.name()} ({medidas.width():.1f} x {medidas.height():.1f} mm)"
            self.combo_tamanos.addItem(texto, tamano.key())
        if seleccionado is not None:
            indice = self.combo_tamanos.findData(seleccionado)
            if indice >= 0:
                self.combo_tamanos.setCurrentIndex(indice)
        self.combo_tamanos.blockSignals(False)

        self.combo_tamanos.setEnabled(len(tamanos) > 0)

        if len(tamanos) == 0:
            self.statusBar.mostrar_aviso("La impresora no reporta tamaños de impresión")

    def on_tamano_cambiado(self, indice: int):
        if indice < 0:
            return
        clave = self.combo_tamanos.itemData(indice)
        if clave is None:
            return
        self.estado.set_tamano_pagina(clave)

    def on_impresora_cambiada(self, nombre: str):
        if nombre is None or nombre == "":
            return
        self.estado.set_impresora(nombre)
        self.refrescar_tamanos()
