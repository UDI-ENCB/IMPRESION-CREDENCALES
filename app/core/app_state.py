from PySide6.QtCore import QObject, QSettings, Signal, qInstallMessageHandler, QtMsgType
from PySide6.QtGui import QPageSize
from PySide6.QtPrintSupport import QPrinterInfo
import logging
import sys

def qt_message_handler(mode, context, message):
    log_message = f"QtContext ({context.file}:{context.line}:{context.function}) -> {message}"

    if mode == QtMsgType.QtDebugMsg:
        logging.debug(log_message)
    elif mode == QtMsgType.QtInfoMsg:
        logging.info(log_message)
    elif mode == QtMsgType.QtWarningMsg:
        logging.warning(log_message)
    elif mode == QtMsgType.QtCriticalMsg:
        logging.critical(log_message)
    elif mode == QtMsgType.QtFatalMsg:
        logging.fatal(log_message)
        sys.exit(1)

class AppState(QObject):

    _instancia = None
    added_data = Signal(dict)
    data_loaded = Signal()
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    def __init__(self):
        if getattr(self, "_inicializado", False):
            return

        super().__init__()
        self._inicializado = True

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s',
            handlers=[
                logging.FileHandler("app_log.log", encoding="utf-8"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        qInstallMessageHandler(qt_message_handler)
        self.settings = QSettings("ENCB","ImpresionCredenciales")

        self.usuario:str | None = self.settings.value("usuario",None, str)
        self.passwd: str | None = self.settings.value("password",None, str)
        self.token: str | None = self.settings.value("token",None, str)
        self.archivo: str | None = self.settings.value("archivo",None, str)
        self.directorio: str | None = self.settings.value("directorio",None, str)
        self.impresora: str | None = self.settings.value("impresora",None, str)
        self.tamano_pagina: str | None = self.settings.value("tamano_pagina",None, str)
        self.datos: list[dict] = []


    def set_user(self, user:str):
        if user.strip() is None:
            return
        self.usuario = user
        self.settings.setValue("usuario", self.usuario)

    def set_cookie(self, cookie:str):
        if cookie.strip() is None:
            return
        self.token = cookie
        self.settings.setValue("token",self.token)

    def set_file(self, file:str|None):
        if isinstance(file, str) or file is None:
            self.archivo = file
            self.settings.setValue("archivo", self.archivo)

    def set_dir(self, dir:str|None):
        if isinstance(dir, str) or dir is None:
            self.directorio = dir
            self.settings.setValue("directorio", self.directorio)

    def set_impresora(self, impresora:str|None):
        if isinstance(impresora, str) and impresora.strip() == "":
            return
        if isinstance(impresora, str) or impresora is None:
            self.impresora = impresora
            self.settings.setValue("impresora", self.impresora)

    @staticmethod
    def impresoras_disponibles() -> list[str]:
        return QPrinterInfo.availablePrinterNames()

    def verificar_impresora(self) -> str | None:
        disponibles = self.impresoras_disponibles()

        if len(disponibles) == 0:
            self.set_impresora(None)
            return None

        if self.impresora not in disponibles:
            self.set_impresora(disponibles[0])

        return self.impresora

    def set_tamano_pagina(self, tamano:str|None):
        if isinstance(tamano, str) and tamano.strip() == "":
            return
        if isinstance(tamano, str) or tamano is None:
            self.tamano_pagina = tamano
            self.settings.setValue("tamano_pagina", self.tamano_pagina)

    @staticmethod
    def tamanos_disponibles(impresora:str|None) -> list[QPageSize]:
        if impresora is None or impresora.strip() == "":
            return []
        info = QPrinterInfo.printerInfo(impresora)
        if info.isNull():
            return []
        return info.supportedPageSizes()

    def verificar_tamano_pagina(self) -> str | None:
        tamanos = self.tamanos_disponibles(self.impresora)

        if len(tamanos) == 0:
            self.set_tamano_pagina(None)
            return None

        claves = [tamano.key() for tamano in tamanos]
        if self.tamano_pagina not in claves:
            self.set_tamano_pagina(claves[0])

        return self.tamano_pagina

    def add_data(self,data:dict):
        self.datos.append(data)

    


        