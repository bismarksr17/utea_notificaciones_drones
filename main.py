from config import DOCKER_NOTIFICACIONES_DRON_ADM
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from config import PATH_XLSX_CONTAC

import sys
sys.path.append('_amigocloud')
from amigocloud import AmigoCloud

# conexion postgress
import psycopg2
import pandas as pd
import time
from datetime import datetime, timedelta
from shapely import wkb
import logging

amigocloud = AmigoCloud(token=DOCKER_NOTIFICACIONES_DRON_ADM)
amigocloud

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# DATOS DE PILOTOS
tecnico_telf = {
    'ALEJANDRO SANCHEZ' : '59178448317@s.whatsapp.net',
    'AURELIO GARCIA' : '59173975475@s.whatsapp.net',
    'DIEGO ARANDIA' : '59162183503@s.whatsapp.net',
    'EDUARDO REYES' : '59175016609@s.whatsapp.net'}

aux_telf = {
    'JOSE ARMANDO CASANOVA' : '59168908131@s.whatsapp.net',
    'MARIO SANCHEZ' : '59175380725@s.whatsapp.net',
    'KARINA DE OLIVEIRA' : '59177437601@s.whatsapp.net',
    'BISMARK SOCOMPI' : '59178194371@s.whatsapp.net'}

def obtener_conexion():
    return psycopg2.connect(
        host=DB_HOST, 
        port=DB_PORT, 
        database=DB_NAME, 
        user=DB_USER, 
        password=DB_PASSWORD)

def insertar_mensaje_whatsapp(cod_canero, nombre_canero, numero_contac, mensaje, enviado=False, fecha_enviado=None):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO notificaciones_wsp.msj_whatsapp (
                cod_canero, nombre_canero, numero_cel, mensaje, enviado, fecha_enviado, numero_contac
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (cod_canero, nombre_canero, 0, mensaje, enviado, fecha_enviado, numero_contac))
        
        conexion.commit()
        cursor.close()
        logging.info("Mensaje insertado correctamente.")
    except Exception as e:
        conexion.rollback()
        logging.exception("Error inesperado")
    return None

# EJECUTAR QUERY
# ejecuta cualquier query sql en el proyecto que se le indique
# requiere el id de proyecto, query a ejecutar y tipo solicitud (get o post)
def ejecutar_query_sql(id_project, query, tipo_sql):
    # define la url del proyecto para ejecutar el querry
    url_proyecto_sql = f'https://app.amigocloud.com/api/v1/projects/{id_project}/sql'
    # crea la estructura de query para amigocloud
    query_sql = {'query': query}
    # variable para almacenar resultado
    resultado_get = ''
    # eleige que tipo de solicitud se realizara (get o post)
    if tipo_sql == 'get': 
        resultado_get = amigocloud.get(url_proyecto_sql, query_sql)
    elif tipo_sql == 'post':
        resultado_get = amigocloud.post(url_proyecto_sql, query_sql)
    else:
        resultado_get = 'Se a seleccionado un tipo de solicitud erroneo.'
    return resultado_get

# CORVERSION DE WKB A COORS
def convertir_wkb(wkb_data):
    return wkb.loads(wkb_data, hex=True)

def get_registro_notificacion_tricho():
    try:
        # get data de nuevas notificacion de liberacion
        query = 'select *, \'tricho\' as origen from dataset_354655 where procesado=false'
        notif = ejecutar_query_sql(33457, query, 'get')
        notif = notif['data']
        # extrae el primer elemento
        return notif
    except Exception as general_err:
        logging.exception("Error inesperado al conectarse a AmigoCloud")
    return None

def get_registro_notificacion_pulv():
    try:
        # get data de nuevas notificacion de liberacion
        query = 'select *, \'pulv\' as origen from dataset_360917 where procesado=false'
        notif = ejecutar_query_sql(35248, query, 'get')
        notif = notif['data']
        # extrae el primer elemento
        return notif
    except Exception as general_err:
        logging.exception("Error inesperado al conectarse a AmigoCloud")
    return None

def anular_registro_notificacion(idd, origen):
    try:
        if origen == 'tricho':
            query = f'update dataset_354655 set procesado = true where id = {idd}'
            exe = ejecutar_query_sql(33457, query, 'post')
            return True
        elif origen == 'pulv':
            query = f'update dataset_360917 set procesado = true where id = {idd}'
            exe = ejecutar_query_sql(35248, query, 'post')
            return True
    except Exception as general_err:
        logging.exception("Error inesperado")
        return False
    return None

def generar_msj_notnull(df_notif_notnull):
    for i, row in df_notif_notnull.iterrows():
        fecha = row['fecha_registro']
        idd = row['id']
        piloto = row['piloto']
        cod_ca = int(row['canhero'].split(' / ')[0])
        canhero = row['canhero'].split(' / ')[1]
        tipo_labor = row['tipo_labor']
        tipo_mensaje = row['tipo_mensaje']
        ubicacion = convertir_wkb(row['ubicacion'])
        longitud = ubicacion.x  # Longitud (coordenada X)
        latitud = ubicacion.y   # Latitud (coordenada Y)
        origen = row['origen']
        
        fecha_str, hora_str = extraer_fecha_hora(fecha)
        
        if piloto in tecnico_telf == False:
            logging.info("El nombre de piloto no esta registrado")
            continue ## NOTIFICAR AL COORDINADOR QUE EL PILOTO NO ESTA EN LA LISTA DE PILOTOS
        
        num_cell = tecnico_telf[piloto]
        num_cell = num_cell[3:11]
        msj = f'''📢 *Mensaje generado automáticamente por el equipo de campo* 📢

👤 Señor(a) *{canhero}*, espero que se encuentre bien.        

🛠️ *Se le informa sobre la siguiente actividad:*
- 🏷️ Estado: *{tipo_mensaje}*
- 🚁 Labor: *{tipo_labor} con drones*
- 📍 Ubicación: [📌 Ver en mapa](https://www.google.com/maps?q={latitud},{longitud})
- 📅 Fecha: *{fecha_str}*
- ⏰ Hora: *{hora_str}*

📞 Para cualquier consulta puede comunicarse con el piloto responsable:
👨‍✈️ *ING. {piloto}* al 📲 *{num_cell}*
'''
        
        nums_validos = get_nums_cells_validos(cod_ca)
        if (len(nums_validos) == 0):
            msj = f'''{piloto} ha registrado {tipo_mensaje} para el trabajo de {tipo_labor} para el cañero {canhero}, sin embargo, el cañero no tiene numeros validos registrados en la lista de contactos'''
            generar_msj_para_coordinador(fecha, idd, msj)
            continue
        
        if anular_registro_notificacion(idd, origen) == False:
            logging.info("Error al anular una notificacion..!!!")
            continue
        
        # registra mensajes para los numeros validos de cañero
        for num in nums_validos:
            #registrar_nuevo_msj(fecha, idd, cod_ca, canhero, num, msj)
            insertar_mensaje_whatsapp(
                cod_canero=cod_ca,
                nombre_canero=canhero,
                numero_contac=f'591{num}@s.whatsapp.net',
                mensaje=msj
            )

        # mensaje para el piloto
        #registrar_nuevo_msj(fecha, idd, 0, piloto, num_cell, msj)
        insertar_mensaje_whatsapp(
            cod_canero=0,
            nombre_canero="GRUPO DRONES",
            numero_contac='120363231867649370@g.us',
            mensaje=msj
        )
    return None

def generar_msj_isnull(df_notif_isnull):
    for i, row in df_notif_isnull.iterrows():
        fecha = row['fecha_registro']
        idd = row['id']
        piloto = row['piloto']
        canhero = row['canhero']
        tipo_labor = row['tipo_labor']
        tipo_mensaje = row['tipo_mensaje']
    
        msj = f'{piloto}, has registrado una notificaion de {tipo_mensaje} de {tipo_labor} sin indicar el cañero, sin nombre del cañero la notificacion no se enviará, vuelve abrir el punto de la notificacion creada y define el cañero'

        if piloto in tecnico_telf:
            num_cell = tecnico_telf[piloto]
            #registrar_nuevo_msj(fecha, idd, 0, piloto, num_cell, msj)
            insertar_mensaje_whatsapp(
                cod_canero=0,
                nombre_canero=piloto,
                numero_contac=num_cell,
                mensaje=msj
            )
            
            # mensaje para coordinador
            msj = f'{piloto} ha registrado una notificaion de {tipo_mensaje} de {tipo_labor} sin indicar el cañero, sin nombre del cañero la notificacion no se enviará'
            generar_msj_para_coordinador(fecha, idd, msj)
        else:
            logging.info("El nombre de piloto no esta registrado")
            continue
    return None

def get_nums_cells_validos(cod_ca):
    df_contac = pd.read_excel(PATH_XLSX_CONTAC)
    df_contac.fillna(0, inplace=True)
    df_contac = df_contac[['cod_ca', 'nom_ca', 'telf01', 'telf02', 'telf03']]
    contac_filtro = df_contac[df_contac['cod_ca']==cod_ca]
    
    if not contac_filtro.empty:  # Verifica si hay al menos una fila
        contac = contac_filtro.iloc[0]
        telefonos = [int(contac['telf01']), int(contac['telf02']), int(contac['telf03'])]
        telefonos_validos = [telefono for telefono in telefonos if len(str(telefono)) == 8]
        return telefonos_validos
    else:
        return [] 
    return None

def extraer_fecha_hora(fecha):
    # Establecer el idioma español
    #locale.setlocale(locale.LC_TIME, "Spanish_Spain.1252")  # Para Windows
    
    dt = datetime.fromisoformat(fecha)
    # Restar 4 horas
    dt_modificado = dt - timedelta(hours=4)

    # Extraer fecha y hora en formato texto
    fecha_str = dt_modificado.strftime("%d de %B de %Y")
    hora_str = dt_modificado.strftime("%I:%M:%S%p")
    return fecha_str, hora_str

def generar_msj_para_coordinador(fecha, idd, msj):
    #registrar_nuevo_msj(fecha, idd, 0, 'JOSE ARMANDO CASANOVA', 68908131, msj)
    insertar_mensaje_whatsapp(
        cod_canero=0,
        nombre_canero='JOSE ARMANDO CASANOVA',
        numero_contac='59168908131@s.whatsapp.net',
        mensaje=msj
    )
    return None

def procesar_notificaciones():
    # obtener notificaciones nuevas
    notif_tricho = get_registro_notificacion_tricho()
    if notif_tricho == None:
        logging.info("Error al ejecuar: def get_registro_notificacion() control biológico")
    # convertir a dataframe

    notif_pulv = get_registro_notificacion_pulv()
    if notif_pulv == None:
        logging.info("Error al ejecuar: def get_registro_notificacion() pulverizacion")
    
    # convertir a dataframe
    notif = notif_tricho + notif_pulv
    df_notif = pd.DataFrame(notif)
    
    # se tienen nuevas notificaciones
    if len(df_notif) > 0:
        # filtrar registros con canero null
        df_notif_isnull = df_notif[df_notif['canhero'].isnull()]
        # filtrar registros con canero notnull
        df_notif_notnull = df_notif[df_notif['canhero'].notnull()]
        # procesar notificaciones con canero null
        if len(df_notif_isnull) > 0:
            generar_msj_isnull(df_notif_isnull)
        # procesar notificaciones con canero notnull
        if len(df_notif_notnull) > 0:
            generar_msj_notnull(df_notif_notnull)
    else:
        logging.info("No existen nuevas notificaciones")
    return None

insertar_mensaje_whatsapp(
    cod_canero=123,
    nombre_canero="Juan Pérez",
    numero_contac="59178194371@s.whatsapp.net",
    mensaje="Este es un mensaje de prueba"
)

while True:
    procesar_notificaciones()
    time.sleep(600)  # 600 segundos = 10 minutos