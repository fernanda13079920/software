import os
from dotenv import load_dotenv                          # Instalar con pip install python-dotenv

load_dotenv()                                           # Cargar todo el cotenido de .env en variables de entorno

#configuración basica que debe tener
class BaseConfig():
    SERVER_NAME = "localhost:5000"
    SECRET_KEY = os.environ.get("SECRET_KEY","")        #clave secreta para la proteccion del login
    DEBUG = True
    TEMPLATE_FOLDER = "views/templates"                 # defino las rutas para los archivos de vista 
    STATIC_FOLDER ="views/static"

# configuracion para la base de datos
class DevConfig(BaseConfig):
    #de la variable de entorno .env traigo todas las configuraciones propias
    DB_HOST = os.environ.get("DB_HOST","")     
    DB_NAME = os.environ.get("DB_NAME","") 
    DB_USER = os.environ.get("DB_USER","") 
    DB_PASS = os.environ.get("DB_PASS","") 
    DB_PORT = os.environ.get("DB_PORT","") 

    #Define la cadena de conexión a tu base de datos PostgreSQL, importante cambiar la contraseñadel postgres en ubuntu
    #SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@localhost:5432/db_diagrama'
    SQLALCHEMY_DATABASE_URI = 'postgresql://'+DB_USER+':'+DB_PASS+'@'+DB_HOST+':'+DB_PORT+'/'+DB_NAME
    #Establece esta opción en False para mejorar el rendimiento.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    print(SQLALCHEMY_DATABASE_URI)
