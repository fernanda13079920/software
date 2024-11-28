from contextlib import contextmanager
import psycopg2
import psycopg2.extras
from config import DevConfig

#----------------------------------para habrir y cerrar las conexiones-----------------------

@contextmanager    #Manejador de contexto, para la conexion
def __get_cursor():
    conexion_db = psycopg2.connect(host = DevConfig.DB_HOST, database = DevConfig.DB_NAME, user = DevConfig.DB_USER, password = DevConfig.DB_PASS, port = DevConfig.DB_PORT)#conexion
    cursor = conexion_db.cursor()   #cursor
    try:
        yield cursor
        conexion_db.commit()
        print('Conexion con la base de datos "Exitosa DESDE CONNECTION"')
    except Exception as ex:
        print(ex)
    finally:
        cursor.close()               #cerramos cursor
        conexion_db.close()          #cerramos conexion
        print("Conexión finalizada")
    print (conexion_db)              #imprimiendo los parametros de conexion


#------------------Realizando llamadas a las consultas y enviando parametros-----------------------
# sacamos el primero, consulta tendra el query: consulta sql , parametros: valores para consulta
#def _fetch_one(consulta:str, parametros: Optional[List[str]]= None):

def _fetch_one(consulta, parametros):      # devolvera el primero
    if parametros is None:
        parametros = []

    with __get_cursor() as cursor:         # hacemos la conexion 
        cursor.execute(consulta,parametros) # hacemos la consulta
        return cursor.fetchone()            # devolvemos el resultado en una tupla
    


def _fetch_all(consulta,parametros):       #dolvera todo
    if parametros is None:
        parametros = []

    with __get_cursor() as cursor:
        cursor.execute(consulta,parametros)
        return cursor.fetchall()


def _fetch_none(consulta,parametros):     #no devuelve
    if parametros is None:
        parametros = []

    with __get_cursor() as cursor:
        cursor.execute(consulta,parametros)


def _fecth_lastrow_id(consulta,parametros):
    if parametros is None:
        parametros = []

    with __get_cursor() as cursor:
        cursor.execute(consulta,parametros)
        return cursor.lastrowid