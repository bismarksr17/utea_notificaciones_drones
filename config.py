import os
from dotenv import load_dotenv

# Cargar .env solo si existe (desarrollo)
if os.path.exists(".env"):
    load_dotenv()   

# API Admin para amigocloud
DOCKER_NOTIFICACIONES_DRON_ADM = os.getenv('DOCKER_NOTIFICACIONES_DRON_ADM')

# Conexion postgress
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Ruta del archivo xlsx con los contactos
PATH_XLSX_CONTAC = os.getenv('PATH_XLSX_CONTAC')

#print(PATH_XLSX_CONTAC)
