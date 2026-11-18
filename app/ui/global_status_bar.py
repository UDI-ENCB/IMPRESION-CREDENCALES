from PySide6.QtWidgets import (
    QStatusBar,
    QLabel,
    QProgressBar,
    QPushButton,
    QWidget,
    QHBoxLayout
)

ERROR_STYLE = """
    color: #B91C1C;
    background-color: rgba(239, 68, 68, 0.12);
    border: 1px solid rgba(239, 68, 68, 0.4);
    border-radius: 4px;
"""

INFO_STYLE = """
    color: #1D4ED8;
    background-color: rgba(37, 99, 235, 0.12);
    border: 1px solid rgba(37, 99, 235, 0.4);
    border-radius: 4px;
"""

SUCCES_STYLE = """
    color: #15803D;
    background-color: rgba(34, 197, 94, 0.12);
    border: 1px solid rgba(34, 197, 94, 0.4);
    border-radius: 4px;
"""

class StatusBarGlobal(QStatusBar):

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Label de avisos (zona izquierda / normal) ---
        self.label_aviso = QLabel("Listo")
        self.label_aviso.setStyleSheet("padding-left: 4px;")
        self.addWidget(self.label_aviso)  # stretch=1 para que ocupe espacio disponible

        self.barra_progreso = QProgressBar()
        self.barra_progreso.setFixedWidth(180)
        self.barra_progreso.setFixedHeight(16)
        self.barra_progreso.setVisible(False)  # oculta hasta que se necesite
        self.addWidget(self.barra_progreso)

    def mostrar_aviso(self, texto: str, duracion_ms: int = 0):
            """Muestra un aviso en el label. Si duracion_ms > 0, se limpia solo."""
            self.label_aviso.setStyleSheet(INFO_STYLE)
            self.label_aviso.setText(texto)
            self.label_aviso.adjustSize()
            self.label_aviso.update()
            if duracion_ms > 0:
                self.showMessage(texto, duracion_ms)  # también dispara messageChanged

    def mostrar_error(self, texto: str, duracion_ms: int = 0):
            """Muestra un aviso en el label. Si duracion_ms > 0, se limpia solo."""
            self.label_aviso.setStyleSheet(ERROR_STYLE)
            self.label_aviso.setText(texto)
            self.label_aviso.adjustSize()
            self.label_aviso.update()
            if duracion_ms > 0:
                self.showMessage(texto, duracion_ms)  # también dispara messageChanged 

    def mostrar_exito(self, texto: str, duracion_ms: int = 0):
            """Muestra un aviso en el label. Si duracion_ms > 0, se limpia solo."""
            self.label_aviso.setStyleSheet(SUCCES_STYLE)
            self.label_aviso.setText(texto)
            self.label_aviso.adjustSize()
            self.label_aviso.update()
            if duracion_ms > 0:
                self.showMessage(texto, duracion_ms)  # también dispara messageChanged

    def limpiar_aviso(self):
        self.label_aviso.setText("Listo")

    def iniciar_progress_bar(self,min:int=0,max:int=100):
        self.barra_progreso.setMinimum(min)
        self.barra_progreso.setMaximum(max)
        self.barra_progreso.setVisible(True)
    def continuar_progreso(self):
        siguiente = self.barra_progreso.value()+1
        if siguiente>=self.barra_progreso.minimum() and siguiente<=self.barra_progreso.maximum():
            self.barra_progreso.setValue(siguiente)

    def stop_progress_bar(self):
        self.barra_progreso.setVisible(False)
        self.barra_progreso.setValue(self.barra_progreso.minimum())

class GlobalState:
    _status_bar_actual : StatusBarGlobal | None = None

    @classmethod
    def registrar(cls, status_bar: StatusBarGlobal):
        cls._status_bar_actual = status_bar

    @classmethod
    def obtener(cls) -> StatusBarGlobal:
        return cls._status_bar_actual