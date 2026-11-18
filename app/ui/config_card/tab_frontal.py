from PySide6.QtWidgets import QLabel

from ui.config_card.widgets_comunes import ElementoImagen, ElementoTexto, TabBase


class TabFrontal(TabBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        ayuda = QLabel(
            "En las leyendas puede usar {tipo} (boleta/empleado) y {adscripcion} "
            "(carrera/departamento); se reemplazan según la categoría del usuario "
            "(ver pestaña Distintivos)."
        )
        ayuda.setWordWrap(True)
        self._lay.addWidget(ayuda)

        self.agregar(ElementoImagen("Fotografía", "frontal/foto", (59, 118, 295, 378)))
        self.agregar(ElementoTexto(
            "Nombre", "frontal/nombre", (390, 142, 591, 94),
            tam=12, negrita=True))
        self.agregar(ElementoTexto(
            "Leyenda del número de usuario", "frontal/num_leyenda", (390, 272, 591, 59),
            texto="Número de {tipo}", tam=7))
        self.agregar(ElementoTexto(
            "Número de usuario", "frontal/num_valor", (390, 331, 591, 71),
            tam=11, negrita=True))
        self.agregar(ElementoTexto(
            "Leyenda de carrera / departamento", "frontal/ads_leyenda", (390, 437, 591, 59),
            texto="{adscripcion}", tam=7))
        self.agregar(ElementoTexto(
            "Carrera / departamento", "frontal/ads_valor", (390, 496, 591, 94),
            multilinea=False, tam=9))
        self.finalizar()