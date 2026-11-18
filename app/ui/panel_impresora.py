from PySide6.QtWidgets import QComboBox, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QGroupBox, QSizePolicy
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

        layout_impresora = QHBoxLayout()
        layout_impresora.addWidget(self.combo_impresoras)
        layout_impresora.addWidget(self.button_refrescar)

        layout = QVBoxLayout()
        layout.addLayout(layout_impresora)

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

    def on_impresora_cambiada(self, nombre: str):
        if nombre is None or nombre == "":
            return
        self.estado.set_impresora(nombre)
