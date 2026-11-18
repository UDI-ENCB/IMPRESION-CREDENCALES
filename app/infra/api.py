from urllib.parse import urljoin
from PySide6.QtGui import QImage
from core.app_state import AppState
from ui.global_status_bar import GlobalState
from pathlib import Path
import httpx
import mimetypes

BASE_URL = 'https://www.siencb.ipn.mx/api/'


async def login(user,password) -> str | None:
    
    url = urljoin(BASE_URL, 'auth/login')
    headers = {'Content-Type':'application/json'}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={'email':user, 'password':password}, headers=headers)
    if response.status_code in [201,200]:
        cookie =  response.cookies['access_token']
        return cookie 
    return None

async def buscar_usuario(numero_usuario:str) -> httpx.Response | None:
    estado = AppState()
    url = urljoin(BASE_URL,'udi-encb/usuarios/buscar' )
    params = {"numero_usuario":numero_usuario}
    cookies = {"access_token":estado.token}
    async with httpx.AsyncClient() as client:
        r = await client.get(url=url, params=params, cookies=cookies)
    return r

async def registrar_impresion(id_usuario:str) -> httpx.Response | None:
    estado = AppState()
    url = urljoin(BASE_URL,f'udi-encb/usuarios/{id_usuario}/impresion' )
    cookies = {"access_token":estado.token}
    async with httpx.AsyncClient() as client:
        r = await client.patch(url=url, cookies=cookies)
    return r

async def descargar_foto(id_usuario: int) -> QImage | None :
    url = urljoin(BASE_URL, f"udi-encb/usuarios/{id_usuario}/foto")
    async with httpx.AsyncClient() as client:
        r = await client.get(url=url)
    if r.status_code != 200:
        return None
    return data_a_qimage(r.content)

async def subir_foto(filename: str,id_usuario:str, path:Path) -> httpx.Response | None:
    ruta_img = Path(path)
    estado = AppState()
    print(locals())
    if ruta_img.is_file() and ruta_img.exists():
        url = urljoin(BASE_URL, f"udi-encb/usuarios/{id_usuario}/foto")
        contentype = mimetypes.guess_type(ruta_img)[0]
        print(filename, url, contentype)
        with ruta_img.open("rb") as img:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    url,
                    files={"file": (filename,img,contentype)},
                    cookies={"access_token":estado.token}
                )
    
        return r
    else:
        return None

def es_webp(datos:bytes) :
    return len(datos)>=12 and datos[:4] == b"RIFF" and datos[8:12] == b"WEBP"

def data_a_qimage( datos:bytes) -> QImage :
    if not es_webp(datos):
        return None
    imagen = QImage()
    if not imagen.loadFromData(datos,"WEBP"):
        return None
    return imagen


