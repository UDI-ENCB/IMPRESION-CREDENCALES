from PySide6.QtCore import QEvent, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QStyledItemDelegate


class AccionesDelegate(QStyledItemDelegate):
    """Dibuja los botones de acciones dentro de una celda de la tabla."""

    eliminar_solicitado = Signal(int)
    accion_secundaria_solicitada = Signal(int)

    MARGEN = 3
    SEPARACION = 4
    ANCHO_BOTON = 26
    ALTO_BOTON = 22

    # (texto, color de fondo, color de borde, habilitado)
    BOTONES = (
        ("❌", QColor(255, 236, 236), QColor(190, 40, 40), True),
        ("📅", QColor(232, 240, 255), QColor(60, 110, 190), True),
    )

    def __init__(self, parent=None):
        super().__init__(parent)

    def _rects(self, rect: QRect):
        alto = min(self.ALTO_BOTON, max(rect.height() - 2 * self.MARGEN, 12))
        y = rect.y() + (rect.height() - alto) // 2
        x = rect.x() + self.MARGEN
        rects = []
        for _ in self.BOTONES:
            rects.append(QRect(x, y, self.ANCHO_BOTON, alto))
            x += self.ANCHO_BOTON + self.SEPARACION
        return rects

    def sizeHint(self, option, index):
        ancho = len(self.BOTONES) * self.ANCHO_BOTON
        ancho += (len(self.BOTONES) - 1) * self.SEPARACION + 2 * self.MARGEN
        return QSize(ancho, self.ALTO_BOTON + 2 * self.MARGEN)

    def paint(self, painter: QPainter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        fondo = index.data(Qt.ItemDataRole.BackgroundRole)
        if fondo is not None:
            painter.fillRect(option.rect, fondo)

        for rect, (texto, color_fondo, color_borde, habilitado) in zip(
                self._rects(option.rect), self.BOTONES):
            painter.setPen(QPen(color_borde, 1))
            painter.setBrush(color_fondo)
            painter.drawRoundedRect(rect.adjusted(0, 0, -1, -1), 4, 4)
            painter.setPen(QColor(60, 60, 60) if habilitado else QColor(170, 170, 170))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, texto)

        painter.restore()

    def editorEvent(self, event, model, option, index):
        if (event.type() == QEvent.Type.MouseButtonRelease
                and event.button() == Qt.MouseButton.LeftButton):
            for boton, rect in enumerate(self._rects(option.rect)):
                if not rect.contains(event.position().toPoint()):
                    continue
                if not self.BOTONES[boton][3]:
                    return True
                if boton == 0:
                    self.eliminar_solicitado.emit(index.row())
                else:
                    self.accion_secundaria_solicitada.emit(index.row())
                return True
        return super().editorEvent(event, model, option, index)
