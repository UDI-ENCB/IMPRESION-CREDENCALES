from PySide6.QtGui import QImage, QPainter, QFont, QColor, QFontMetrics, QTransform
from PySide6.QtCore import Qt, QRectF, QPoint, QRect
import segno
from ui.global_status_bar import GlobalState
from pathlib import Path
from os.path import join
from ui.config_card.ajustes import obtener_ajustes
from infra.api import descargar_foto

DPI_FRENTE = 96

def pt_to_px(pts):
    return pts / 25.4  * DPI_FRENTE

async def renderizar_frente(data : dict) -> QImage:
    ajustes = obtener_ajustes()
    statusBar = GlobalState.obtener()
    if not data.get("encontrado"):
        statusBar.mostrar_error("Informacion del usuario no obtenida")
        return None

    if not data.get("fotografia"):
        statusBar.mostrar_error("El usuario no cuenta con fotografia")
        

    

    w, h  = ajustes.value("general/ancho_px",0), ajustes.value("general/alto_px")

    #Cargando tamaño de la imagen
    imagen = QImage(int(w), int(h), QImage.Format_ARGB32)
    imagen.fill(Qt.white)

    # Cargar ruta plantilla frontal
    carpeta = ajustes.value("general/carpeta_plantilla", None)
    fondo_frontal = ajustes.value("general/fondo_frontal", None)

    if carpeta is None or fondo_frontal is None:
        statusBar.mostrar_error("No se pudo obtener las rutas delfondo")
        return None

    ruta_front = Path(join(carpeta, fondo_frontal))
    if not ruta_front.exists() or not ruta_front.is_file():
        statusBar.mostrar_error("No se encontro la plantilla frontal")

    # Creando painter para cargar imagen
    try:
        p = QPainter(imagen)
        p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)

        # Pintando plantilla frontal
        p.drawImage(imagen.rect(), QImage(ruta_front))

        #Cargar fotografia de usuario

        x = int(ajustes.value("frontal/foto/x"))
        y = int(ajustes.value("frontal/foto/y"))
        w = int(ajustes.value("frontal/foto/w"))
        h = int(ajustes.value("frontal/foto/h"))
        caja_foto = QRectF(x,y,w,h)
        foto = await descargar_foto(data["id"])
        if not isinstance(foto, QImage):
            foto = QImage(w,h,QImage.Format_ARGB32)
            foto.fill(Qt.gray)
        foto = foto.scaled(caja_foto.size().toSize(), Qt.KeepAspectRatio,Qt.SmoothTransformation)
        p.drawImage(caja_foto.topLeft(),foto)

        #Pintamos nombre del usuario

        nombre = data["nombre_completo"]
        nombre_fuente = ajustes.value("frontal/nombre/fuente")
        tamanio_nombre = int(ajustes.value("frontal/nombre/tam"))
        color_nombre = ajustes.value("frontal/nombre/color")
        x_nombre = int(ajustes.value("frontal/nombre/x"))
        y_nombre = int(ajustes.value("frontal/nombre/y"))
        w_nombre = int(ajustes.value("frontal/nombre/w"))
        h_nombre = int(ajustes.value("frontal/nombre/h"))
        bold_nombre = ajustes.value("frontal/nombre/negrita")
        if not isinstance(bold_nombre, bool):
            bold_nombre = str(bold_nombre).lower() == "true"

        pintar_texto(p, nombre, nombre_fuente, color_nombre, tamanio_nombre, (x_nombre,y_nombre,w_nombre,h_nombre), bold_nombre)

        # Pintamos Numero de {tipo}
        
        tipo = data["tipo_usuario"]
        distintivos = buscar_categoria(ajustes, tipo)
        if distintivos is None:
            statusBar.mostrar_error("No se encontro al tipo de usuario verificar la configuracion.")
            return None
        texto = str(ajustes.value("frontal/num_leyenda/texto")).replace("{tipo}",distintivos["tipo"])
        leyenda_fuente = ajustes.value("frontal/num_leyenda/fuente")
        tamanio_num_leyenda = ajustes.value("frontal/num_leyenda/tam")
        color_leyenda = ajustes.value("frontal/num_leyenda/color")
        x_num_leyenda = int(ajustes.value("frontal/num_leyenda/x"))
        y_num_leyenda = int(ajustes.value("frontal/num_leyenda/y"))
        w_num_leyenda = int(ajustes.value("frontal/num_leyenda/w"))
        h_num_leyenda = int(ajustes.value("frontal/num_leyenda/h"))

        bold_leyenda = ajustes.value("frontal/num_leyenda/negrita")
        if not isinstance(bold_leyenda, bool):
            bold_leyenda = str(bold_leyenda).lower() == "true"
        pintar_texto(p,texto,leyenda_fuente,color_leyenda,tamanio_num_leyenda,(x_num_leyenda,y_num_leyenda,w_num_leyenda,h_num_leyenda),bold_leyenda)


        #Pintamos el numero_usuario

        numero_usuario = data["numero_usuario"]
        nombre_fuente = ajustes.value("frontal/num_valor/fuente")
        tamanio_nombre = int(ajustes.value("frontal/num_valor/tam"))
        color_nombre = ajustes.value("frontal/num_valor/color")
        x_nombre = int(ajustes.value("frontal/num_valor/x"))
        y_nombre = int(ajustes.value("frontal/num_valor/y"))
        w_nombre = int(ajustes.value("frontal/num_valor/w"))
        h_nombre = int(ajustes.value("frontal/num_valor/h"))
        bold_nombre = ajustes.value("frontal/num_valor/negrita")
        if not isinstance(bold_nombre, bool):
            bold_nombre = str(bold_nombre).lower() == "true"
        pintar_texto(p, numero_usuario, nombre_fuente, color_nombre, tamanio_nombre, (x_nombre,y_nombre,w_nombre,h_nombre), bold_nombre)

        # Puntamos la leyenda de adcripcion
        texto_adscripcion = distintivos["adscripcion"]
        leyenda_fuente = ajustes.value("frontal/ads_leyenda/fuente")
        tamanio_num_leyenda = ajustes.value("frontal/ads_leyenda/tam")
        color_leyenda = ajustes.value("frontal/ads_leyenda/color")
        x_num_leyenda = int(ajustes.value("frontal/ads_leyenda/x"))
        y_num_leyenda = int(ajustes.value("frontal/ads_leyenda/y"))
        w_num_leyenda = int(ajustes.value("frontal/ads_leyenda/w"))
        h_num_leyenda = int(ajustes.value("frontal/ads_leyenda/h"))

        bold_leyenda = ajustes.value("frontal/ads_leyenda/negrita")
        if not isinstance(bold_leyenda, bool):
            bold_leyenda = str(bold_leyenda).lower() == "true"
        pintar_texto(p,texto_adscripcion,leyenda_fuente,color_leyenda,tamanio_num_leyenda,(x_num_leyenda,y_num_leyenda,w_num_leyenda,h_num_leyenda),bold_leyenda)


        #Pintamos Area

        numero_usuario = data["area"]
        nombre_fuente = ajustes.value("frontal/ads_valor/fuente")
        tamanio_nombre = int(ajustes.value("frontal/ads_valor/tam"))
        color_nombre = ajustes.value("frontal/ads_valor/color")
        x_nombre = int(ajustes.value("frontal/ads_valor/x"))
        y_nombre = int(ajustes.value("frontal/ads_valor/y"))
        w_nombre = int(ajustes.value("frontal/ads_valor/w"))
        h_nombre = int(ajustes.value("frontal/ads_valor/h"))
        bold_nombre = ajustes.value("frontal/ads_valor/negrita")
        if not isinstance(bold_nombre, bool):
            bold_nombre = str(bold_nombre).lower() == "true"
        pintar_texto(p, numero_usuario, nombre_fuente, color_nombre, tamanio_nombre, (x_nombre,y_nombre,w_nombre,h_nombre), bold_nombre)

        nombre_imagen = distintivos["archivo"]
        if nombre_imagen is None or nombre_imagen == "":
            statusBar.mostrar_error("No se pudo obtenete el nombre del distintivo del usuario")
            return None

        imagen_nombre_distintivo = Path(join(carpeta,nombre_imagen))
        if not imagen_nombre_distintivo.exists() or not imagen_nombre_distintivo.is_file():
            statusBar.mostrar_error("El nombre del distintivo no existe o no es un archivo.")

        imagen_distintivo = QImage(imagen_nombre_distintivo)
        x_distintivo = int(ajustes.value("distintivos/mascara/x"))
        y_distintivo = int(ajustes.value("distintivos/mascara/y"))
        w_distintivo = int(ajustes.value("distintivos/mascara/w"))
        h_distintivo = int(ajustes.value("distintivos/mascara/h"))

        p.drawImage(QPoint(x_distintivo,  y_distintivo), imagen_distintivo)



        
        statusBar.mostrar_exito("Frontal generado")
        return imagen
    finally:
        if isinstance(p,QPainter):
            p.end()


async def renderizar_posterior(data:dict)->QImage:
    ajustes = obtener_ajustes()
    statusBar = GlobalState.obtener()
    if not data.get("encontrado"):
        statusBar.mostrar_error("Informacion del usuario no obtenida")
        return None
    w, h  = ajustes.value("general/ancho_px",0), ajustes.value("general/alto_px")
    
    #Cargando tamaño de la imagen
    imagen = QImage(int(w), int(h), QImage.Format_ARGB32)
    imagen.fill(Qt.white)

    # Cargar ruta plantilla trasera
    carpeta = ajustes.value("general/carpeta_plantilla", None)
    fondo_reverso = ajustes.value("general/fondo_trasero", None)

    if carpeta is None or fondo_reverso is None:
        statusBar.mostrar_error("No se pudo obtener las rutas delfondo")
        return None

    ruta_reverso = Path(join(carpeta, fondo_reverso))
    if not ruta_reverso.exists() or not ruta_reverso.is_file():
        statusBar.mostrar_error("No se encontro la plantilla frontal")

    # Creando painter para cargar imagen
    try:
        p = QPainter(imagen)
        p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)

        # Pintando plantilla frontal
        p.drawImage(imagen.rect(), QImage(ruta_reverso))


        # Pintar distintivo
        tipo = data["tipo_usuario"]
        distintivos = buscar_categoria(ajustes, tipo)
        nombre_imagen = distintivos["archivo"]
        if nombre_imagen is None or nombre_imagen == "":
            statusBar.mostrar_error("No se pudo obtenete el nombre del distintivo del usuario")
            return None

        imagen_nombre_distintivo = Path(join(carpeta,nombre_imagen))
        if not imagen_nombre_distintivo.exists() or not imagen_nombre_distintivo.is_file():
            statusBar.mostrar_error("El nombre del distintivo no existe o no es un archivo.")

        imagen_distintivo = QImage(imagen_nombre_distintivo)
        x_distintivo = int(ajustes.value("distintivos/mascara/x"))
        y_distintivo = int(ajustes.value("distintivos/mascara/y"))
        w_distintivo = int(ajustes.value("distintivos/mascara/w"))
        h_distintivo = int(ajustes.value("distintivos/mascara/h"))

        p.drawImage(QPoint(x_distintivo,  y_distintivo), imagen_distintivo)

        # Pintar titulo
        titulo = ajustes.value("trasera/titulo/texto")
        fuente_titulo = ajustes.value("trasera/titulo/fuente")
        color_titulo = ajustes.value("trasera/titulo/color")
        tam_titulo = int(ajustes.value("trasera/titulo/tam"))
        x_titulo = int(ajustes.value("trasera/titulo/x"))
        y_titulo = int(ajustes.value("trasera/titulo/y"))
        w_titulo = int(ajustes.value("trasera/titulo/w"))
        h_titulo = int(ajustes.value("trasera/titulo/h"))
        bold_titulo = ajustes.value("trasera/titulo/negrita")
        if not isinstance(bold_titulo, bool):
                bold_titulo = str(bold_titulo).lower() == "true"
        alineacion_titulo = ajustes.value("trasera/titulo/alineacion")
        
        pintar_texto(p, titulo,fuente_titulo,color_titulo,tam_titulo,(x_titulo,y_titulo,w_titulo,h_titulo),bold_titulo, alineacion=alineacion_titulo)


        # Pintar aviso
        cuerpo = ajustes.value("trasera/cuerpo/texto")
        fuente_cuerpo = ajustes.value("trasera/cuerpo/fuente")
        color_cuerpo = ajustes.value("trasera/cuerpo/color")
        tam_cuerpo = int(ajustes.value("trasera/cuerpo/tam"))
        x_cuerpo = int(ajustes.value("trasera/cuerpo/x"))
        y_cuerpo = int(ajustes.value("trasera/cuerpo/y"))
        w_cuerpo = int(ajustes.value("trasera/cuerpo/w"))
        h_cuerpo = int(ajustes.value("trasera/cuerpo/h"))
        bold_cuerpo = ajustes.value("trasera/cuerpo/negrita")
        if not isinstance(bold_cuerpo, bool):
                    bold_cuerpo = str(bold_cuerpo).lower() == "true"
        alineacion_cuerpo = ajustes.value("trasera/cuerpo/alineacion")
        pintar_texto(p, cuerpo,fuente_cuerpo,color_cuerpo,tam_cuerpo,(x_cuerpo,y_cuerpo,w_cuerpo,h_cuerpo),bold_cuerpo, alineacion=alineacion_cuerpo)
        

        # Pintar firma del dicrector. 
        nombre_firma = ajustes.value("trasera/firma/archivo")
        archivo_firma = Path(join(carpeta,nombre_firma))

        if not archivo_firma.exists() or not archivo_firma.is_file():
            statusBar.mostrar_error("No se encontro la firma del director")
            return None

        x_firma = int(ajustes.value("trasera/firma/x"))
        y_firma = int(ajustes.value("trasera/firma/y"))
        w_firma = int(ajustes.value("trasera/firma/w"))
        h_firma = int(ajustes.value("trasera/firma/h"))

        caja_firma = QRectF(x_firma, y_firma,w_firma, h_firma)
        firma_img = QImage(archivo_firma)
        if firma_img.isNull():
            statusBar.mostrar_error("No se pudo cargar la firma del director")
            return None
        # Escalar la firma al tamano de la caja conservando el aspect ratio
        firma_img = firma_img.scaled(
            caja_firma.size().toSize(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        p.drawImage(caja_firma.topLeft(), firma_img)

        # Pintar aviso
        director = ajustes.value("trasera/director/texto")
        fuente_director = ajustes.value("trasera/director/fuente")
        color_director = ajustes.value("trasera/director/color")
        tam_director = int(ajustes.value("trasera/director/tam"))
        x_director = int(ajustes.value("trasera/director/x"))
        y_director = int(ajustes.value("trasera/director/y"))
        w_director = int(ajustes.value("trasera/director/w"))
        h_director = int(ajustes.value("trasera/director/h"))
        bold_director = ajustes.value("trasera/director/negrita")
        if not isinstance(bold_director, bool):
                    bold_director = str(bold_director).lower() == "true"
        alineacion_director = ajustes.value("trasera/director/alineacion")
        pintar_texto(p, director,fuente_director,color_director,tam_director,(x_director,y_director,w_director,h_director),bold_director, alineacion=alineacion_director)

        # Pintamos QR
        num_usuario = data.get("numero_usuario",None)
        if num_usuario is None:
            statusBar.mostrar_error("No se encontro el numero de usuario para generar el QR")
            return None
        texto_qr = f"USUARIO={num_usuario} | https://siencb.ipn.mx/verificar_usuario?numero_usuario={num_usuario}"
        x_qr = int(ajustes.value("trasera/qr/x"))
        y_qr = int(ajustes.value("trasera/qr/y"))
        w_qr = int(ajustes.value("trasera/qr/w"))
        h_qr = int(ajustes.value("trasera/qr/h"))

        caja_qr = QRectF(x_qr,y_qr,w_qr,h_qr)
        dibujar_qr(p,texto_qr,caja_qr)
        p.end()
        statusBar.mostrar_exito("Frontal generado")
        return imagen
    finally:
        if isinstance(p, QPainter):
            p.end()


def pintar_texto(
        pincel: QPainter,
        texto:str,
        fuente:str,
        color:str,
        tamanio: int,
        position: tuple,
        bold: bool,
        tamanio_minimo: int = 8,
        alineacion = "izquierda"
):
    
    pincel.setPen(QColor(color))
    caja_texto = QRectF(*position)

    # El texto inicia en el borde superior de la caja, alineado con la foto.
    y_inicio = caja_texto.top()

    # Auto-ajuste: se reduce el tamaño SOLO hasta tamanio_minimo para intentar
    # que quepa en una sola linea; si aun asi no cabe, se permite el wrap.
    bajo, alto = min(tamanio_minimo, tamanio), tamanio
    while bajo < alto:
        medio = (bajo + alto + 1) // 2
        fuente_prueba = QFont(fuente)
        fuente_prueba.setPixelSize(pt_to_px(medio))
        fuente_prueba.setBold(bold)
        if QFontMetrics(fuente_prueba).horizontalAdvance(texto) <= caja_texto.width():
            bajo = medio
        else:
            alto = medio - 1

    fuente_texto = QFont(fuente)
    fuente_texto.setPixelSize(pt_to_px(bajo))
    fuente_texto.setBold(bold)
    pincel.setFont(fuente_texto)

    rect_texto = QRectF(caja_texto.left(), y_inicio, caja_texto.width(), caja_texto.bottom() - y_inicio)

    flags = Qt.TextWordWrap | Qt.AlignTop
    if alineacion == "izquierda":
        flags = flags  | Qt.AlignLeft
    if alineacion == "centro":
        flags = flags | Qt.AlignCenter
    if alineacion == "derecha":
        flags = flags | Qt.AlignRight
    pincel.drawText(rect_texto, flags, texto)

def buscar_categoria(s, nombre_buscar)->dict|None:
    cantidad = s.beginReadArray("distintivos/categorias")
    resultado = None

    for i in range(cantidad):
        s.setArrayIndex(i)
        nombre = s.value("nombre", "")

        if nombre == nombre_buscar:
            resultado = {
                "nombre": nombre,
                "archivo": s.value("archivo", ""),
                "tipo": s.value("tipo", ""),
                "adscripcion": s.value("adscripcion", ""),
            }
            break

    s.endArray()
    return resultado

def dibujar_qr(p:QPainter, texto:str, caja: QRectF, error="m"):
    qr = segno.make(texto, error=error)
    matriz = [list(fila) for fila in qr.matrix]
    n = len(matriz)
    lado = min(caja.width(), caja.height()) / n

    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(Qt.black)

    for y, fila  in enumerate(matriz):
        for x, v in enumerate(fila):
            if v:
                p.drawRect(QRectF(caja.x()+x*lado, caja.y()+y*lado, lado, lado))
    p.restore()          

async def dibujar_frente(p:QPainter, data:dict, rect: QRect):
    frente = await renderizar_frente(data)

    if frente is None or not isinstance(frente, QImage):
        return False

    horizontal = True
    if horizontal:
        transform = QTransform()
        transform.rotate(90)
        frente = frente.transformed(transform)
    # Se ajusta al alto de la pagina; el ancho sobrante se recorta a los lados.
    frente_escalado = frente.size().scaled(
        rect.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding
    )


    rect_centrado = QRect(QPoint(0,0),frente_escalado)
    rect_centrado.moveCenter(rect.center())

    p.drawImage(rect_centrado, frente )

async def dibujar_reverso(p:QPainter, data:dict, rect: QRect):
    reverso = await renderizar_posterior(data)

    if reverso is None or not isinstance(reverso, QImage):
        return False

    horizontal = True
    if horizontal:
        transform = QTransform()
        transform.rotate(90)
        reverso = reverso.transformed(transform)
    # Se ajusta al alto de la pagina; el ancho sobrante se recorta a los lados.
    reverso_rescalado = reverso.size().scaled(
        rect.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding
    )



    rect_centrado = QRect(QPoint(0,0),reverso_rescalado)
    rect_centrado.moveCenter(rect.center())

    p.drawImage(rect_centrado, reverso )
    