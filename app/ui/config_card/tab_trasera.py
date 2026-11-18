from ui.config_card.widgets_comunes import ElementoImagen, ElementoTexto, TabBase


class TabTrasera(TabBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.agregar(ElementoImagen("Código QR", "trasera/qr", (59, 59, 295, 295)))
        self.agregar(ElementoTexto(
            "Título del texto", "trasera/titulo", (413, 59, 531, 71),
            texto="Aviso", tam=9, negrita=True))
        self.agregar(ElementoTexto(
            "Contenido del texto", "trasera/cuerpo", (413, 142, 531, 236),
            texto="Texto informativo de la credencial.", multilinea=True,
            tam=6, alineacion="izquierda"))
        self.agregar(ElementoImagen(
            "Firma del director", "trasera/firma", (354, 390, 307, 118),
            archivo="firma_director.png"))
        self.agregar(ElementoTexto(
            "Nombre y cargo del director", "trasera/director", (236, 520, 543, 94),
            texto="Nombre del Director\nCargo del Director", multilinea=True,
            tam=7, alineacion="centro"))
        self.finalizar()