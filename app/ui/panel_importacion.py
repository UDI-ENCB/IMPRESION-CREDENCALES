from PySide6.QtWidgets import QFileDialog, QLineEdit, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QGroupBox, QSizePolicy, QCheckBox, QRadioButton, QButtonGroup, QLabel
from qasync import asyncSlot
from core.app_state import AppState
from services.load_data import LoaderInfo
from services.filtros import filtrar, eliminar_registro, actualizar_registro
from ui.global_status_bar import GlobalState


class InportPanel(QWidget):


    def __init__(self):
        super().__init__()
        self.estado =  AppState()
        self.statusBar = GlobalState.obtener()
        self.button_chose_file = QPushButton("Seleccionar")
        self.button_chose_file.clicked.connect(self.select_file)
        self.button_clean_file = QPushButton("Limpiar")
        

        self.button_chose_dir = QPushButton("Seleccionar")
        self.button_chose_dir.clicked.connect(self.select_dir)
        self.button_clean_dir = QPushButton("Limpiar")

        self.line_file = QLineEdit(placeholderText="C:/Users/user/Archivo.xlsx")
        self.line_file.setReadOnly(True)
        if not self.estado.archivo is None or not self.estado.archivo == '':
            self.line_file.setText(self.estado.archivo)
        self.button_clean_file.clicked.connect(self.line_file.clear)

        self.line_dir = QLineEdit(placeholderText="C:/Fotos")
        self.line_dir.setReadOnly(True)
        if not self.estado.directorio is None or not self.estado.directorio == '':
            self.line_dir.setText(self.estado.directorio)
        self.button_clean_dir.clicked.connect(self.line_dir.clear)

        layaout_file = QHBoxLayout()
        layaout_file.addWidget(self.line_file)
        layaout_file.addWidget(self.button_chose_file)
        layaout_file.addWidget(self.button_clean_file)

        layout_dir = QHBoxLayout()
        layout_dir.addWidget(self.line_dir)
        layout_dir.addWidget(self.button_chose_dir)
        layout_dir.addWidget(self.button_clean_dir)

        self.button_load_info = QPushButton("Cargar")
        self.button_load_info.clicked.connect(self.load_info)
        self.button_refiltrar = QPushButton("Refiltrar")
        self.button_refiltrar.clicked.connect(self.refiltrar)

        layout_botones = QHBoxLayout()
        layout_botones.addWidget(self.button_load_info)
        layout_botones.addWidget(self.button_refiltrar)

        layout = QVBoxLayout()
        layout.addLayout(layaout_file)
        layout.addLayout(layout_dir)
        layout.addLayout(layout_botones)


        group_box = QGroupBox("Cargar Datos")
        group_box.setLayout(layout)

        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(group_box)
        layout_principal.addWidget(self._crear_grupo_filtros())
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def _crear_grupo_filtros(self) -> QGroupBox:
        grupo = QGroupBox("Filtros")
        layout = QHBoxLayout(grupo)
        columna_izquierda = QVBoxLayout()
        columna_derecha = QVBoxLayout()

        self.check_filtros = QCheckBox("Activar filtros")
        self.check_filtros.setChecked(self.estado.filtros.get("activos", True))
        self.check_filtros.toggled.connect(self._on_filtros_toggled)
        columna_izquierda.addWidget(self.check_filtros)

        self.radio_impresion = self._crear_grupo_radios(
            columna_izquierda, "Fecha de impresion",
            (("todos", "Todos"), ("impresos", "Impresos"), ("sin_imprimir", "Sin imprimir")),
            self.estado.filtros.get("impresion", "todos"))
        self.radio_foto = self._crear_grupo_radios(
            columna_izquierda, "Fotografia",
            (("todos", "Todos"), ("con", "Con foto"), ("sin", "Sin foto")),
            self.estado.filtros.get("foto", "todos"))

        self.radio_remplazo = self._crear_grupo_radios(
            columna_derecha, "Reemplazo de foto",
            (("todos", "Todos"), ("con", "Con reemplazo"), ("sin", "Sin reemplazo")),
            self.estado.filtros.get("remplazo", "todos"))

        self.check_encontrados = QCheckBox("Solo registros encontrados")
        self.check_encontrados.setChecked(self.estado.filtros.get("solo_encontrados", True))
        columna_derecha.addWidget(self.check_encontrados)

        self.label_resumen = QLabel("")
        columna_derecha.addWidget(self.label_resumen)
        columna_derecha.addStretch()

        layout.addLayout(columna_izquierda)
        layout.addLayout(columna_derecha)

        self._actualizar_resumen()
        self._actualizar_estado_filtros()
        return grupo

    def _crear_grupo_radios(self, layout: QVBoxLayout, titulo: str, opciones, valor: str) -> QButtonGroup:
        layout.addWidget(QLabel(titulo))
        grupo = QButtonGroup(self)
        fila = QHBoxLayout()
        for clave, texto in opciones:
            radio = QRadioButton(texto)
            radio.setProperty("clave", clave)
            radio.setChecked(clave == valor)
            grupo.addButton(radio)
            fila.addWidget(radio)
        fila.addStretch()
        layout.addLayout(fila)
        return grupo

    def _valor_radio(self, grupo: QButtonGroup, defecto: str) -> str:
        boton = grupo.checkedButton()
        if boton is None:
            return defecto
        return boton.property("clave")

    def _leer_filtros(self) -> dict:
        return {
            "activos": self.check_filtros.isChecked(),
            "impresion": self._valor_radio(self.radio_impresion, "todos"),
            "foto": self._valor_radio(self.radio_foto, "todos"),
            "remplazo": self._valor_radio(self.radio_remplazo, "todos"),
            "solo_encontrados": self.check_encontrados.isChecked(),
        }

    def _on_filtros_toggled(self, activo: bool):
        self._actualizar_estado_filtros()

    def _actualizar_estado_filtros(self):
        activo = self.check_filtros.isChecked()
        for grupo in (self.radio_impresion, self.radio_foto, self.radio_remplazo):
            for boton in grupo.buttons():
                boton.setEnabled(activo)
        self.check_encontrados.setEnabled(activo)
        self.button_refiltrar.setEnabled(activo)

    def _actualizar_resumen(self):
        total = len(self.estado.datos_todos)
        visibles = len(self.estado.datos)
        if total == 0:
            self.label_resumen.setText("Sin registros cargados")
        else:
            self.label_resumen.setText(f"Mostrando {visibles} de {total} registros")

    def _aplicar_filtros(self) -> bool:
        self.estado.filtros = self._leer_filtros()
        self.estado.datos = filtrar(
            self.estado.datos_todos, self.estado.filtros, self.estado.directorio)
        self._actualizar_resumen()
        self.estado.data_loaded.emit()
        return True

    @asyncSlot()
    async def refiltrar(self):
        if not self.estado.datos_todos:
            self._actualizar_resumen()
            self.statusBar.mostrar_aviso("No hay registros cargados para refiltrar")
            return
        self._aplicar_filtros()
        self.statusBar.mostrar_exito(
            f"Filtros aplicados: {len(self.estado.datos)} de {len(self.estado.datos_todos)} registros")

    @asyncSlot()
    async def select_file(self):
        file = QFileDialog.getOpenFileName(self,caption="Selecciona la lista",filter="*.xlsx *.csv")
        if not file[0] is None and not file[0] == '':
            self.line_file.setText(file[0])
            self.estado.set_file(self.line_file.text())

    @asyncSlot()
    async def select_dir(self):
        dir = QFileDialog.getExistingDirectory(self,caption="Selecciona directorio de imgs")
        if dir and not dir == '':
            self.line_dir.setText(dir)
            self.estado.set_dir(self.line_dir.text())

    @asyncSlot()
    async def load_info(self):
        self.estado.filtros = self._leer_filtros()
        loader = LoaderInfo()
        await loader.load_info_from_file()
        self._actualizar_resumen()
        self.estado.data_loaded.emit()

    def limpiar_file(self):
        self.line_file.clear()
        self.estado.set_file(None)

    def limpiar_dir(self):
        self.line_dir.clear()
        self.estado.set_dir(None)
