
from openpyxl import load_workbook, Workbook
from core.app_state import AppState
from ui.global_status_bar import GlobalState
from infra.api import buscar_usuario
from services.filtros import filtrar
from pathlib import Path
import asyncio
from os.path import join



class LoaderInfo:

    def __init__(self):
        self.estado = AppState()
        self.statu_bar = GlobalState.obtener()

    async def load_info_from_file(self):
        if self.estado.archivo is None or self.estado.archivo.strip() == '':
            self.statu_bar.mostrar_error("Archivo no seleccionado")
            return

        path = Path(self.estado.archivo)

        if not path.exists or not path.is_file:
            self.statu_bar.mostrar_error("No se encontro el archivo")
            return

        wb = await asyncio.to_thread(load_workbook, path)
        try:
            if not "FOTOS" in wb.sheetnames:
                self.statu_bar.mostrar_error("El Workbook no contiene la hoja FOTOS")
                return

            photos_sheet = wb["FOTOS"]
            i = 0

            numeros_usuario = None

            for columm in photos_sheet.iter_cols():
                columm_name = columm[0].value
                if columm_name == "BOLETA":
                    numeros_usuario = columm
                    break

            if numeros_usuario is None:
                self.statu_bar.mostrar_error("No se encontro la columna BOLETA en el Workbook")
                return

            self.statu_bar.mostrar_aviso("Buscando informacion de los usuarios")
            self.statu_bar.iniciar_progress_bar(max=len(numeros_usuario))
            
            usuarios_encontrados=0
            usuarios_no_encontrados = 0
            error = False
            self.estado.datos.clear()
            for cell in numeros_usuario:
                
                registro_usuario = await self.buscar_registro_usuario(cell.value)
                if registro_usuario is None:
                    error = True
                    break
                if isinstance(registro_usuario, bool) and registro_usuario == False:
                    continue
                if registro_usuario.get("encontrado",False):
                    usuarios_encontrados += 1
                else:
                    usuarios_no_encontrados +=1
                self.estado.datos.append(registro_usuario)
                
            self.statu_bar.stop_progress_bar()
            if not error:
                self.estado.datos_todos = list(self.estado.datos)
                self.estado.datos = filtrar(
                    self.estado.datos_todos, self.estado.filtros, self.estado.directorio)
                self.estado.logger.info(f"Operacion completada: Encontrados: {usuarios_encontrados} | No Encontrados: {usuarios_no_encontrados}")
                self.statu_bar.mostrar_aviso(f"Operacion completada: Encontrados: {usuarios_encontrados} | No Encontrados: {usuarios_no_encontrados}")
                self.estado.data_loaded.emit()
        finally:
            wb.close()

    async def buscar_registro_usuario(self, numero_usuario:str)-> dict | bool | None:
        self.statu_bar.continuar_progreso()
        valor = str(numero_usuario).strip().upper()
        
        if valor is None or valor == '' or valor == 'BOLETA' or valor == 'NONE':
            return False
        
        registro_usuarios = await buscar_usuario(valor.strip().upper())
        if registro_usuarios.status_code == 403:
            self.estado.logger.info("Usuario no autenticado al cargar data.")
            self.statu_bar.mostrar_error("Usuario no aunteticado")
            return None
        
        if registro_usuarios.status_code == 400:
            
            registro_usuario = {
                "encontrado": False,
                "numero_usuario": valor.strip().upper(),
            }
            return registro_usuario
            
        if not registro_usuarios.status_code in [200,400,403]:
            self.estado.logger.info(f"Error al traer el registro del servidor: {valor}")
            self.statu_bar.mostrar_error(f"Error inesperado: status:{registro_usuarios.status_code}")
            return None
        if registro_usuarios.status_code == 200:
            registro_dict = registro_usuarios.json()
            registro_usuario = {
                "encontrado": True,
                "numero_usuario": registro_dict["numero_usuario"],
                "nombre_completo": registro_dict["nombre_completo"],
                "area": registro_dict["area"],
                "tipo_usuario":registro_dict["tipo_usuario"],
                "curp":registro_dict["curp"],
                "id":registro_dict["id"],
                "fecha_impresion": registro_dict["fecha_impresion"],
                "checked":False
            }
            nombre_foto = registro_dict["nombre_fotografia"]
            if nombre_foto is None or nombre_foto == '':
                registro_usuario["fotografia"] = False
            else:
                registro_usuario["fotografia"] = True
            registro_usuario["remplazo_foto"] = False
            if not self.estado.directorio is None and not self.estado.directorio == '':
                archivo = Path(join(self.estado.directorio, f"{registro_dict["numero_usuario"]}.jpg"))
                if archivo.exists() and archivo.is_file():
                    registro_usuario["remplazo_foto"] = True
            return registro_usuario