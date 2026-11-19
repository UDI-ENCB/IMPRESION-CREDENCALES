from PySide6.QtWidgets import QStackedLayout, QSplitter, QTableView, QGroupBox, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QHeaderView, QTextEdit, QWidget, QLabel
from PySide6.QtGui import Qt, QPixmap, QImage,QPageLayout, QPageSize, QPainter, QPdfWriter
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSizeF, QMarginsF
from PySide6.QtPrintSupport import QPrinter, QPrinterInfo
from PySide6.QtPdf import QPdfDocument
from qasync import asyncSlot
from core.table_model import TableModel
from core.app_state import AppState
from ui.config_card.ajustes import obtener_ajustes
from ui.global_status_bar import GlobalState
from infra.api import subir_foto, registrar_impresion
from templates.generador_imgs import renderizar_frente, renderizar_posterior, dibujar_frente, dibujar_reverso
from os.path import join
from pathlib import Path
from services.load_data import LoaderInfo
import asyncio
from infra.impresora_win import estado_impresora, ids_en_cola, esperar_trabajo


alto_mm=85.98
ancho_mm=54.02
CARPETA_TEMP = Path(__file__).resolve().parents[2] / "assets" / "temp"
class WorkPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.estado = AppState()
        self.statusBar = GlobalState.obtener()
    
        

        # Definimos tabla.
        self.grupo_tabla = QGroupBox("Registros")
        self.layout_tabla = QVBoxLayout(self.grupo_tabla)

        self.line_agregar_registro = QLineEdit(placeholderText="2026500111")
        self.line_agregar_registro.returnPressed.connect(self.on_click_agregar_registro)
        self.button_agregar_registro = QPushButton("Agregar Registro")
        self.button_agregar_registro.clicked.connect(self.on_click_agregar_registro)
        layout_agregar_registro = QHBoxLayout()
        layout_agregar_registro.addWidget(self.line_agregar_registro)
        layout_agregar_registro.addWidget(self.button_agregar_registro)

        self.layout_tabla.addLayout(layout_agregar_registro)

        self.tabla = QTableView()
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        self.tabla_modelo = None
        self.tabla.setSelectionBehavior(QTableView.SelectRows)
        self.tabla.setSelectionMode(QTableView.SingleSelection)
        self.tabla.clicked.connect(self.on_clikc_row)
        
        #self.tabla.setHorizontalHeaderLabels(["Seleccion","Nombre", "Foto", "Fecha Impreion", "Acciones"])
        #self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.layout_tabla.addWidget(self.tabla)

        #Definimos vista previa

        self.grupo_preview = QGroupBox("Vista Previa")
        self.stackt_preview = QStackedLayout(self.grupo_preview)

        self.texto_preview = QTextEdit()
        self.texto_preview.setReadOnly(True)
        self.texto_preview.setPlaceholderText("Selecciona o marca elementos en la tabla...")
        self.stackt_preview.addWidget(self.texto_preview)

        self.pagina_imgs = QWidget()
        layout_img = QVBoxLayout(self.pagina_imgs)

        # Las dos imágenes van apiladas en vertical, con una pequeña separación.
        # Los labels no se estiran (toman el tamaño de su imagen) y se alinean al
        # centro horizontal; los "stretch" por arriba y por abajo las centran
        # verticalmente en el contenedor.
        columna_imgs = QVBoxLayout()
        columna_imgs.setSpacing(12)

        self.lado_frente = QLabel("Frente")
        self.lado_reverso = QLabel("Reverso")
        for lbl in (self.lado_frente, self.lado_reverso):
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setMinimumSize(200, 130)
            columna_imgs.addWidget(lbl, 0, Qt.AlignHCenter)

        layout_img.addStretch(1)
        layout_img.addLayout(columna_imgs, 0)
        layout_img.addStretch(1)

        fila_botones = QHBoxLayout()
        columna_botones = QVBoxLayout()
        self.button_imprimir = QPushButton("Imprimir")
        self.button_imprimir.clicked.connect(self.on_clik_imprimir)
        self.button_reintentar = QPushButton("Reintentar")
        self.button_subir_foto = QPushButton("Subir Foto")
        self.button_subir_foto.setEnabled(False)
        self.button_subir_foto.clicked.connect(self.on_click_subir_img)
        fila_botones.addWidget(self.button_imprimir)
        fila_botones.addWidget(self.button_reintentar)
        columna_botones.addLayout(fila_botones)
        columna_botones.addWidget(self.button_subir_foto)
        layout_img.addLayout(columna_botones)

        self.stackt_preview.addWidget(self.pagina_imgs)

        self.stackt_preview.setCurrentIndex(0)

        #Botones de acciones
        self.subir_img_select = QPushButton("Subir fotos seleccionadas")
        self.subir_img_select.clicked.connect(self.on_click_subir_img_select)
        self.subir_img_todas = QPushButton("Subir todas las fotos")
        self.subir_img_todas.clicked.connect(self.on_click_subir_todas_imgs)
        self.imp_credenciales_select = QPushButton("Imprimir credenciales seleccionadas")
        self.imp_credenciales_select.clicked.connect(self.on_clicl_imprimir_select)
        self.cancelar_impresiones = QPushButton("Cancelar")
        self.cancelar_impresiones.clicked.connect(self.on_click_cancelar_impresion)
        self.cancelar_impresiones.setEnabled(False)
        self._cancelar_impresion = False

        botones_acciones_layout = QHBoxLayout()
        botones_acciones_layout.addWidget(self.subir_img_select)
        botones_acciones_layout.addWidget(self.subir_img_todas)
        botones_acciones_layout.addWidget(self.imp_credenciales_select)
        botones_acciones_layout.addWidget(self.cancelar_impresiones)

        #Configuramos spliter

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.grupo_tabla)
        self.splitter.addWidget(self.grupo_preview)

        self.splitter.setSizes([600,300])

        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(self.splitter)
        layout_principal.addLayout(botones_acciones_layout)

        self.estado.data_loaded.connect(self.set_table_model)

    def set_table_model(self):
        self.tabla_modelo = TableModel()
        self.tabla.setModel(self.tabla_modelo)
        #self.tabla.selectionModel().currentRowChanged.connect(self.on_select_row)

    def on_header_clicked(self,section):
        if section == 0:
            self.tabla_modelo.toogle_all_checked()

    @asyncSlot()
    async def on_click_agregar_registro(self):
        numero_usuario = self.line_agregar_registro.text().strip().upper()
        if numero_usuario == "":
            self.statusBar.mostrar_aviso("Ingresa un numero de usuario")
            return

        ya_existe = any(
            str(datos.get("numero_usuario", "")).strip().upper() == numero_usuario
            for datos in self.estado.datos
        )
        if ya_existe:
            self.statusBar.mostrar_aviso(f"El usuario {numero_usuario} ya esta en la tabla")
            return

        self.button_agregar_registro.setEnabled(False)
        self.line_agregar_registro.setEnabled(False)
        try:
            # El loader avanza la barra de progreso; conservamos su valor actual.
            valor_progreso = self.statusBar.barra_progreso.value()
            registro = await LoaderInfo().buscar_registro_usuario(numero_usuario)
            self.statusBar.barra_progreso.setValue(valor_progreso)
        finally:
            self.button_agregar_registro.setEnabled(True)
            self.line_agregar_registro.setEnabled(True)

        if registro is None:
            self.statusBar.mostrar_error("No se pudo consultar al usuario")
            return
        if registro is False:
            self.statusBar.mostrar_aviso("Ingresa un numero de usuario valido")
            return
        if not registro.get("encontrado", False):
            self.statusBar.mostrar_error(f"El usuario {numero_usuario} no existe")
            return

        if self.tabla_modelo is None:
            self.set_table_model()
        self.tabla_modelo.add_row(registro)
        self.tabla.scrollToBottom()
        self.line_agregar_registro.clear()
        self.statusBar.mostrar_exito(f"Usuario {registro.get('numero_usuario', numero_usuario)} agregado")

    @asyncSlot()
    async def on_clikc_row(self, index: QModelIndex):
        fila = index.row()
        numero_usuario = index.siblingAtColumn(0).data()  # valor de la columna 0 de esa fila

        ajustes = obtener_ajustes()

        # Obtenemos la data del usuario
        datos_usuario = [u for u in self.estado.datos if u["numero_usuario"] == numero_usuario]
        if len(datos_usuario) == 0:
            self.statusBar.mostrar_error("No se encontro al usuario")
            return

        img_front = await renderizar_frente(datos_usuario[0])
        self.stackt_preview.setCurrentIndex(1)
        if isinstance(img_front, QImage):
            self.mostrar_imagen(self.lado_frente, QPixmap.fromImage(img_front))
        else:
            self.stackt_preview.setCurrentIndex(0)
            return

        img_reverso = await renderizar_posterior(datos_usuario[0])
        if isinstance(img_reverso, QImage):
            self.mostrar_imagen(self.lado_reverso, QPixmap.fromImage(img_reverso))
        else:
            self.stackt_preview.setCurrentIndex(0)
            return

        if datos_usuario[0]["remplazo_foto"]:
            self.button_subir_foto.setEnabled(True)
        else:
            self.button_subir_foto.setEnabled(False)

    @asyncSlot()
    async def on_click_subir_img(self):
        indice = self.tabla.currentIndex()
        if not indice.isValid():
            self.statusBar.mostrar_error("Fila no valida")
            return
        
        fila = indice.siblingAtColumn(0).data()
        usuario_id = [u.get("id", "-1") for u in self.estado.datos if u.get("numero_usuario","") == fila ]
        if len(usuario_id) == 0:
            self.statusBar.mostrar_error("No se encontro al usuario")
            return
        
        file_name = f"{fila}.jpg"
        ruta = Path(join(self.estado.directorio, file_name))
        await self.subir_imagen(file_name, usuario_id[0],ruta, indice.row())


    async def subir_imagen(self, file_name:str, usuario_id:str,ruta:Path, indice:int):
        
        response = await subir_foto(file_name, usuario_id, ruta)
        if response is None:
            self.statusBar.mostrar_error("La ruta de la imagen no es un archivo o no existe")
            return
        if not response.status_code in [200,203]:
            self.statusBar.mostrar_aviso(response.text)
            return
        self.statusBar.mostrar_exito("Imagen subida correctamente")

        # Bucamos al usuario de nuevo.
        loader = LoaderInfo()
        registro_usuario = await loader.buscar_registro_usuario(file_name.split(".")[0])
        if registro_usuario is None or registro_usuario is False:
            self.statusBar.mostrar_error("No se encontro al usuario")
            return

        self.tabla_modelo.update_row(indice,registro_usuario)
        

    @asyncSlot()
    async def on_click_subir_img_select(self):
        indices=[]
        seleccionados = []
        for index,datos in enumerate(self.estado.datos):
            if datos.get("checked", False):
                if datos.get("encontrado",False):
                    seleccionados.append(datos)
                    indices.append(index)
        self.statusBar.iniciar_progress_bar(max=len(seleccionados))
        for index,registro in enumerate(seleccionados):
            if registro.get("remplazo_foto",False):
                usuario_id = registro.get("id","-1")
                file_name = f"{registro["numero_usuario"]}.jpg"
                ruta = Path(join(self.estado.directorio, file_name))
                await self.subir_imagen(file_name, usuario_id, ruta, indices[index])
                self.statusBar.continuar_progreso()
        self.statusBar.stop_progress_bar()

    @asyncSlot()
    async def on_click_subir_todas_imgs(self):
        self.statusBar.iniciar_progress_bar(max=len(self.estado.datos))
        for index, registro in enumerate(self.estado.datos):
            if registro.get("encontrado",False):
                if registro.get("remplazo_foto",False):
                    usuario_id = registro.get("id","-1")
                    file_name = f"{registro["numero_usuario"]}.jpg"
                    ruta = Path(join(self.estado.directorio, file_name))
                    await self.subir_imagen(file_name, usuario_id, ruta, index)
                    self.statusBar.continuar_progreso()
        self.statusBar.stop_progress_bar()

    def on_click_cancelar_impresion(self):
        self._cancelar_impresion = True
        self.cancelar_impresiones.setEnabled(False)
        self.statusBar.mostrar_aviso("Cancelando impresiones...")

    @asyncSlot()
    async def on_clicl_imprimir_select(self):
        indices=[]
        seleccionados = []
        for index,datos in enumerate(self.estado.datos):
            if datos.get("checked", False):
                if datos.get("encontrado",False):
                    seleccionados.append(datos)
                    indices.append(index)

        if not seleccionados:
            self.statusBar.mostrar_aviso("No hay registros seleccionados")
            return

        self._cancelar_impresion = False
        self.imp_credenciales_select.setEnabled(False)
        self.cancelar_impresiones.setEnabled(True)
        self.statusBar.iniciar_progress_bar(max=len(seleccionados))
        impresas = 0
        try:
            for posicion, registro in enumerate(seleccionados):
                if self._cancelar_impresion:
                    break
                if not registro.get("fotografia", False):
                    self.statusBar.continuar_progreso()
                    continue
                if not await self.imprimir_credencial(indices[posicion]):
                    break
                impresas += 1
                if not await self.actualizar_registro_impreso(indices[posicion], registro):
                    break
                self.statusBar.mostrar_aviso(f"Credencial {registro.get("numero_usuario","XXXXXX")} impresa")
                self.statusBar.continuar_progreso()
                
                await asyncio.sleep(0)
        finally:
            self.statusBar.stop_progress_bar()
            self.imp_credenciales_select.setEnabled(True)
            self.cancelar_impresiones.setEnabled(False)

        if self._cancelar_impresion:
            self.statusBar.mostrar_aviso(f"Impresion cancelada. {impresas} credencial(es) impresas")

    async def actualizar_registro_impreso(self, fila: int, registro: dict) -> bool:
        """Registra la impresion en la API y refresca la fila de la tabla."""
        id_usuario = registro.get("id")
        if id_usuario is None:
            self.statusBar.mostrar_error("No se pudo registrar la impresion: el registro no tiene id")
            return False

        try:
            respuesta = await registrar_impresion(str(id_usuario))
        except Exception as exc:
            self.statusBar.mostrar_error(f"No se pudo registrar la impresion: {exc}")
            return False

        if respuesta is None:
            self.statusBar.mostrar_error("No se pudo registrar la impresion: sin respuesta")
            return False
        if respuesta.status_code not in (200, 201):
            self.statusBar.mostrar_error(f"No se pudo registrar la impresion: status {respuesta.status_code}")
            return False

        numero_usuario = registro.get("numero_usuario")
        if numero_usuario is None:
            return True

        # El loader avanza la barra de progreso; conservamos su valor actual.
        valor_progreso = self.statusBar.barra_progreso.value()
        registro_nuevo = await LoaderInfo().buscar_registro_usuario(numero_usuario)
        self.statusBar.barra_progreso.setValue(valor_progreso)

        if not isinstance(registro_nuevo, dict):
            return True

        registro_nuevo["checked"] = registro.get("checked", False)
        if self.tabla_modelo is not None:
            self.tabla_modelo.update_row(fila, registro_nuevo)
        return True


    
    def _tamano_pagina_configurado(self) -> QPageSize:
        """Devuelve el perfil de tamaño guardado en la configuracion.

        Si la clave guardada no existe en la lista del driver actual se usa el
        tamaño CR80 personalizado, que es el que corresponde a la credencial.
        """
        clave = self.estado.tamano_pagina
        if clave is not None:
            for tamano in AppState.tamanos_disponibles(self.estado.impresora):
                if tamano.key() == clave:
                    return tamano
        return QPageSize(QSizeF(ancho_mm, alto_mm), QPageSize.Millimeter, "Credit Card")

    async def generar_pdf_credencial(self, index_registro: int) -> Path | None:
        data_usuario = self.estado.datos[index_registro]
        if data_usuario is None or data_usuario.get("encontrado",False) == False or data_usuario.get("fotografia", False) == False:
            self.statusBar.mostrar_error("El usuario o su fotografia no fueron encontrados.")
            return None

        CARPETA_TEMP.mkdir(parents=True, exist_ok=True)
        numero_usuario = data_usuario.get("numero_usuario","registro")
        ruta_pdf = CARPETA_TEMP / f"credencial_{numero_usuario}.pdf"

        writer = QPdfWriter(str(ruta_pdf))
        writer.setResolution(800)
        writer.setPageLayout(QPageLayout(QPageSize(QSizeF(ancho_mm, alto_mm), QPageSize.Millimeter, "Credit Card"),
                                        QPageLayout.Portrait, QMarginsF(0,0,0,0)))
        writer.setTitle(f"Credencial {numero_usuario}")

        p = QPainter()
        if not p.begin(writer):
            self.statusBar.mostrar_error("No se pudo crear el PDF de la credencial")
            return None
        try:
            rect = p.viewport()
            await dibujar_frente(p,data_usuario,rect)
            writer.newPage()
            await dibujar_reverso(p,data_usuario,rect)
        finally:
            p.end()

        return ruta_pdf

    async def imprimir_credencial(self, index_registro: int) -> bool:
        impresora = self.estado.impresora
        if not isinstance(impresora, str):
            self.statusBar.mostrar_error("El nombre de la impresora es incorrecto")
            return False
        if impresora is None or  impresora.strip() == "":
            self.statusBar.mostrar_error("Nombre de la impresora incorrecto")
            return False

        #Configuramos impresora
        info = next((i for i in QPrinterInfo.availablePrinters() if i.printerName() == impresora), None)

        if info is None:
            self.statusBar.mostrar_error(f"No se econtro la impresora: {impresora}")
            return False

        if self._cancelar_impresion:
            return False

        # Verificacion previa: estado publicado por el driver.
        estado = estado_impresora(impresora)
        if not estado.ok:
            self.statusBar.mostrar_error(estado.mensaje)
            return False

        # Ids ya en cola, para reconocer el trabajo propio despues.
        try:
            ids_previos = ids_en_cola(impresora)
        except OSError as exc:
            self.statusBar.mostrar_aviso(f"No se pudo leer la cola: {exc}")
            ids_previos = set()

        ruta_pdf = await self.generar_pdf_credencial(index_registro)
        if ruta_pdf is None:
            return False

        if self._cancelar_impresion:
            return False

        printer = QPrinter(info, QPrinter.HighResolution)
        printer.setResolution(300)
        printer.setFullPage(True)
        tamano = self._tamano_pagina_configurado()
        response = printer.setPageLayout(QPageLayout(tamano,
                                        QPageLayout.Portrait, QMarginsF(0,0,0,0)))
        if not response:
            self.statusBar.mostrar_aviso(f"La impresora no acepto {tamano.name()}, se uso {printer.pageLayout().pageSize().name()}")
        printer.setColorMode(QPrinter.Color)

        doblecara = True
        if doblecara:
            printer.setDuplex(QPrinter.DuplexMode.DuplexLongSide)

        documento = QPdfDocument()
        documento.load(str(ruta_pdf))
        if documento.pageCount() == 0:
            self.statusBar.mostrar_error("No se pudo leer el PDF generado")
            return False

        p = QPainter()
        if not p.begin(printer):
            self.statusBar.mostrar_error("No se pudo iniciar la impresora")
            return False
        try:
            rect = p.viewport()
            for pagina in range(documento.pageCount()):
                if pagina > 0:
                    printer.newPage()
                imagen_pagina = documento.render(pagina, rect.size())
                p.drawImage(rect, imagen_pagina)
        finally:
            p.end()
            documento.close()

        if printer.printerState() == QPrinter.PrinterState.Error:
            self.statusBar.mostrar_error("La impresora rechazo el trabajo")
            return False

        # Espera a que el trabajo salga de la cola. La impresora lo mantiene
        # listado mientras imprime, asi que el fin es su salida de la cola.
        resultado = await esperar_trabajo(
            impresora,
            ids_previos,
            cancelar=lambda: self._cancelar_impresion,
        )
        if not resultado.ok:
            if resultado.cancelado:
                self.statusBar.mostrar_aviso(resultado.mensaje)
            else:
                self.statusBar.mostrar_error(resultado.mensaje)
            return False

        self.statusBar.mostrar_exito(f"Credencial impresa y guardada en {ruta_pdf}")
        return True

    @asyncSlot()
    async def on_clik_imprimir(self):
        index = self.tabla.currentIndex()
        if not index.isValid():
            self.statusBar.mostrar_aviso("Selecciona un registro de la tabla")
            return

        fila = index.row()
        if not 0 <= fila < len(self.estado.datos):
            self.statusBar.mostrar_error("El registro seleccionado no es valido")
            return

        registro = self.estado.datos[fila]
        if not registro.get("encontrado", False):
            self.statusBar.mostrar_error("El usuario no fue encontrado")
            return
        if not registro.get("fotografia", False):
            self.statusBar.mostrar_error("El usuario no tiene fotografia")
            return

        # La impresion individual no se cancela: solo se limpia la bandera que
        # pudo quedar activa despues de cancelar un lote.
        self._cancelar_impresion = False
        self.button_imprimir.setEnabled(False)
        self.imp_credenciales_select.setEnabled(False)
        try:
            if not await self.imprimir_credencial(fila):
                return
            if not await self.actualizar_registro_impreso(fila, registro):
                return
            self.statusBar.mostrar_exito(f"Credencial {registro.get('numero_usuario','XXXXXX')} impresa")
        finally:
            self.button_imprimir.setEnabled(True)
            self.imp_credenciales_select.setEnabled(True)


    def mostrar_imagen(self, label: QLabel, pixmap: QPixmap):
        """Escala la imagen a las dimensiones objetivo del contenedor (las mismas
        para ambas caras), conservando la relación de aspecto. Así las dos imágenes
        quedan con exactamente el mismo tamaño, sin distorsión."""
        ancho_obj, alto_obj = self._dimensiones_objetivo()
        label.setPixmap(
            pixmap.scaled(
                ancho_obj, alto_obj,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def _dimensiones_objetivo(self):
        """Tamaño máximo (ancho, alto en píxeles) para cada imagen basado en el
        espacio disponible del contenedor de la vista previa."""
        ancho = max(200, self.pagina_imgs.width() - 24)
        alto = max(130, (self.pagina_imgs.height() - 60) // 2)
        return ancho, alto
        
        


    

    




class RegistroUsuario(QAbstractTableModel):
    def __init__(self,datos):
        super().__init__()
        self._datos = datos
        self._columnas = ["","numero_usuario","nombre_completo", "fecha_impresion","nombre_fotografia"]

    def rowCount(self, parent = QModelIndex()):
        return len(self._datos)

    def columnCount(self, parent = QModelIndex()):
        return 6

    def data(self, index, role = Qt.ItemDataRole.DisplayRole):
        if(role == Qt.ItemDataRole.DisplayRole and index.column() > 0):
            fila = self._data[index.row()]
            return fila[self._columnas[index.column()]]

        if(role == Qt.ItemDataRole.CheckStateRole and index.column() == 0):
            return Qt.CheckState.Checked

