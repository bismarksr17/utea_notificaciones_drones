# config.py
from dotenv import load_dotenv
import os
load_dotenv(override=True)

# CONSTANTES

# API Admin para amigocloud
DOCKER_NOTIFICACIONES_DRON_ADM = os.getenv('DOCKER_NOTIFICACIONES_DRON_ADM')

# Conexion postgress
POSTGRES_UTEA = {
    "HOST": os.getenv("HOST"),
    "PORT": os.getenv("PORT"),
    "DATABASE": os.getenv("DATABASE"),
    "USER": os.getenv("USER"),
    "PASSWORD": os.getenv("PASSWORD"),
}