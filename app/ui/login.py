from PySide6.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QSystemTrayIcon, QGroupBox,QSizePolicy
from infra.api import login
from qasync import asyncSlot
from ui.global_status_bar import GlobalState
from core.app_state import AppState

class Login(QWidget):
    
    def __init__(self):
        super().__init__()

        self.estado = AppState()
        self.statusBar = GlobalState.obtener()
        self.user_edit = QLineEdit( placeholderText="correo@ejemplo.com")
        self.password_edit = QLineEdit(echoMode=QLineEdit.EchoMode.Password, placeholderText="Clave super secreta")
        self.connect_push = QPushButton('Conectar')

        self.connect_push.clicked.connect(self.verificar_usuario)
        if not self.estado.usuario is None:
            self.user_edit.setText(self.estado.usuario)
        layout = QHBoxLayout()
        layout.addWidget(self.user_edit)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.connect_push)

        group_login = QGroupBox("Incio de sesion")
        group_login.setLayout(layout)

        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(group_login)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    @asyncSlot()
    async def verificar_usuario(self):

        
        password = self.password_edit.text()
        usuario = self.user_edit.text()
        res = await login(usuario,password)
        tray = QSystemTrayIcon()
        tray.show
        message = ''
        if res is None:
            self.estado.logger.info("No se pudo verificar al usuario")
            self.statusBar.mostrar_exito( 'No se pudo verificar al usuario')
        else:
            self.estado.logger.info("Usuario verificado")
            self.statusBar.mostrar_exito('Usuario verificado')
            self.estado.set_user(usuario)
            self.estado.set_cookie(res)
        
        tray.showMessage('Verificacion ejecutada',message, QSystemTrayIcon.Information, 3000 )




        