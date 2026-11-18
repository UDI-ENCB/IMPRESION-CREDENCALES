from PySide6.QtWidgets import (
    QFileDialog, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from ui.config_card.widgets_comunes import ElementoImagen, TabBase, ruta_relativa

CATEGORIAS_DEFECTO = [
    ("Licenciatura", "distintivo_licenciatura.png", "boleta", "Carrera"),
    ("Posgrado", "distintivo_posgrado.png", "boleta", "Programa"),
    ("Docente", "distintivo_docente.png", "empleado", "Departamento"),
    ("Personal de apoyo", "distintivo_apoyo.png", "empleado", "Departamento"),
]
COLUMNAS = ["Categoría", "Archivo de máscara", "Valor {tipo}", "Valor {adscripcion}"]


class TabDistintivos(TabBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.carpeta = ""

        # Posición/tamaño común a todas las máscaras
        self.mascara = ElementoImagen(
            "Posición y tamaño de la máscara (igual para todas)",
            "distintivos/mascara", (709, 35, 260, 260))
        self.agregar(self.mascara)

        # Tabla de categorías
        gb = QGroupBox("Categorías de usuario")
        lay = QVBoxLayout(gb)
        lay.addWidget(QLabel(
            "Los archivos de máscara se buscan dentro de la carpeta de plantilla."))
        self.tabla = QTableWidget(0, len(COLUMNAS))
        self.tabla.setHorizontalHeaderLabels(COLUMNAS)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setMinimumHeight(200)
        lay.addWidget(self.tabla)

        botones = QHBoxLayout()
        b_add = QPushButton("Agregar")
        b_del = QPushButton("Eliminar")
        b_file = QPushButton("Elegir máscara...")
        b_add.clicked.connect(lambda: self._agregar_fila())
        b_del.clicked.connect(self._eliminar_fila)
        b_file.clicked.connect(self._elegir_mascara)
        for b in (b_add, b_del, b_file):
            botones.addWidget(b)
        botones.addStretch()
        lay.addLayout(botones)

        self._lay.addWidget(gb)
        self.finalizar()

    def set_carpeta(self, carpeta):
        super().set_carpeta(carpeta)
        self.carpeta = carpeta

    def _agregar_fila(self, valores=("", "", "", "")):
        r = self.tabla.rowCount()
        self.tabla.insertRow(r)
        for c, v in enumerate(valores):
            self.tabla.setItem(r, c, QTableWidgetItem(v))

    def _eliminar_fila(self):
        r = self.tabla.currentRow()
        if r >= 0:
            self.tabla.removeRow(r)

    def _elegir_mascara(self):
        r = self.tabla.currentRow()
        if r < 0:
            return
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar máscara", self.carpeta,
            "Imágenes (*.png *.jpg *.jpeg)")
        if ruta:
            self.tabla.setItem(r, 1, QTableWidgetItem(ruta_relativa(ruta, self.carpeta)))

    def _llenar(self, categorias):
        self.tabla.setRowCount(0)
        for fila in categorias:
            self._agregar_fila(fila)

    def cargar(self, s):
        super().cargar(s)
        n = s.beginReadArray("distintivos/categorias")
        categorias = []
        for i in range(n):
            s.setArrayIndex(i)
            categorias.append((
                str(s.value("nombre", "")), str(s.value("archivo", "")),
                str(s.value("tipo", "")), str(s.value("adscripcion", ""))))
        s.endArray()
        self._llenar(categorias if n > 0 else CATEGORIAS_DEFECTO)

    def guardar(self, s):
        super().guardar(s)
        s.remove("distintivos/categorias")
        filas = []
        for r in range(self.tabla.rowCount()):
            fila = [(self.tabla.item(r, c).text().strip() if self.tabla.item(r, c) else "")
                    for c in range(4)]
            if fila[0]:
                filas.append(fila)
        s.beginWriteArray("distintivos/categorias", len(filas))
        for i, (nombre, archivo, tipo, ads) in enumerate(filas):
            s.setArrayIndex(i)
            s.setValue("nombre", nombre)
            s.setValue("archivo", archivo)
            s.setValue("tipo", tipo)
            s.setValue("adscripcion", ads)
        s.endArray()

    def restablecer(self):
        super().restablecer()
        self._llenar(CATEGORIAS_DEFECTO)