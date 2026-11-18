from PySide6.QtWidgets import QFileDialog, QLineEdit, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QGroupBox, QSizePolicy
from qasync import asyncSlot
from core.app_state import AppState
from services.load_data import LoaderInfo


class InportPanel(QWidget):


    def __init__(self):
        super().__init__()
        self.estado =  AppState()
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

        layout = QVBoxLayout()
        layout.addLayout(layaout_file)
        layout.addLayout(layout_dir)
        layout.addWidget(self.button_load_info)


        group_box = QGroupBox("Cargar Datos")
        group_box.setLayout(layout)

        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(group_box)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

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
        loader = LoaderInfo()
        await loader.load_info_from_file()
        self.estado.data_loaded.emit()

    def limpiar_file(self):
        self.line_file.clear()
        self.estado.set_file(None)

    def limpiar_dir(self):
        self.line_dir.clear()
        self.estado.set_dir(None)