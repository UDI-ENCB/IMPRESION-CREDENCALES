from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QPushButton, QScrollArea
from ui.login import Login
from ui.panel_importacion import InportPanel
from ui.panel_impresora import PrinterPanel
from ui.panel_trabajo import WorkPanel
from ui.global_status_bar import StatusBarGlobal, GlobalState
from core.app_state import AppState
from qasync import QEventLoop
import sys
import asyncio
from ui.config_card.ventana_configuracion import VentanaConfiguracion
app = QApplication()
loop = QEventLoop(app)
asyncio.set_event_loop(loop)
estado = AppState()
status_bar = StatusBarGlobal()
GlobalState.registrar(status_bar)

ventana_config = VentanaConfiguracion()
config_card_button = QPushButton("⚙️")
config_card_button.clicked.connect(ventana_config.show)
login = Login()
panel_importacion = InportPanel()
panel_impresora = PrinterPanel()
panel_trabajo = WorkPanel()

layout = QVBoxLayout()
layout.addWidget(config_card_button)
layout.addWidget(login)
layout.addWidget(panel_importacion)
layout.addWidget(panel_impresora)
layout.addWidget(panel_trabajo, 1)
widget = QWidget()
widget.setLayout(layout)

scroll = QScrollArea()
scroll.setWidgetResizable(True)
scroll.setWidget(widget)

window = QMainWindow()
window.setStatusBar(status_bar)
window.setWindowTitle("Impresion credenciales")
window.setCentralWidget(scroll)

window.show()

with loop:
    loop.run_forever()