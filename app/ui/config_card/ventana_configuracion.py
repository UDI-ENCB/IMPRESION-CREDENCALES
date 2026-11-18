from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QMessageBox, QPushButton, QTabWidget, QVBoxLayout,
)

from ui.config_card.ajustes import obtener_ajustes
from ui.config_card.tab_distintivos import TabDistintivos
from ui.config_card.tab_frontal import TabFrontal
from ui.config_card.tab_general import TabGeneral
from ui.config_card.tab_trasera import TabTrasera


class VentanaConfiguracion(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de credencial")
        self.resize(680, 760)

        self.tab_general = TabGeneral()
        self.tab_frontal = TabFrontal()
        self.tab_trasera = TabTrasera()
        self.tab_distintivos = TabDistintivos()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.tab_general, "General")
        self.tabs.addTab(self.tab_frontal, "Parte frontal")
        self.tabs.addTab(self.tab_trasera, "Parte trasera")
        self.tabs.addTab(self.tab_distintivos, "Distintivos")

        botones = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btn_reset = QPushButton("Restablecer pestaña")
        botones.addButton(btn_reset, QDialogButtonBox.ResetRole)
        botones.accepted.connect(self._guardar)
        botones.rejected.connect(self.reject)
        btn_reset.clicked.connect(self._restablecer_actual)

        lay = QVBoxLayout(self)
        lay.addWidget(self.tabs)
        lay.addWidget(botones)

        # Propagar tamaño y carpeta a las pestañas dependientes
        self._dependientes = (self.tab_frontal, self.tab_trasera, self.tab_distintivos)
        self.tab_general.dimensionesCambiadas.connect(self._propagar_dimensiones)
        self.tab_general.carpetaCambiada.connect(self._propagar_carpeta)

        self._cargar_todo()

    def _propagar_dimensiones(self, ancho, alto):
        for t in self._dependientes:
            t.set_dimensiones(ancho, alto)

    def _propagar_carpeta(self, carpeta):
        for t in self._dependientes:
            t.set_carpeta(carpeta)

    def _cargar_todo(self):
        s = obtener_ajustes()
        self.tab_general.cargar(s)  # primero: define límites y carpeta
        for t in self._dependientes:
            t.cargar(s)

    def _guardar(self):
        carpeta = self.tab_general.ed_carpeta.text().strip()
        if not carpeta:
            QMessageBox.warning(self, "Falta carpeta",
                                "Seleccione la carpeta de la plantilla.")
            self.tabs.setCurrentWidget(self.tab_general)
            return
        s = obtener_ajustes()
        self.tab_general.guardar(s)
        for t in self._dependientes:
            t.guardar(s)
        s.sync()
        self.accept()

    def _restablecer_actual(self):
        actual = self.tabs.currentWidget()
        if QMessageBox.question(
            self, "Restablecer", "¿Restablecer los valores de esta pestaña?"
        ) == QMessageBox.Yes:
            actual.restablecer()