from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget


class GrupoColapsable(QGroupBox):
    """QGroupBox que oculta su contenido al desmarcar el titulo."""

    def __init__(self, titulo: str, parent=None):
        super().__init__(titulo, parent)
        self.setCheckable(True)
        self.setChecked(True)

        self._contenido = QWidget()
        externo = QVBoxLayout(self)
        externo.setContentsMargins(0, 0, 0, 0)
        externo.addWidget(self._contenido)

        self.toggled.connect(self._on_toggled)

    def set_contenido(self, layout):
        """Asigna el layout que se muestra u oculta con el titulo."""
        self._contenido.setLayout(layout)

    def _on_toggled(self, activo: bool):
        self._contenido.setVisible(activo)
        self.updateGeometry()
