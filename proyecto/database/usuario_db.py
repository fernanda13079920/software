from flask import session
from ..models.User import User 
from datetime import datetime
from .connection import _fetch_all,_fecth_lastrow_id,_fetch_none,_fetch_one  #las funciones 


# Crear un nuevo usuario
def create(usuario: User) -> User:
    # Consulta SQL para insertar un nuevo usuario en la tabla 'users'
    sql = "INSERT INTO users (name, email, password_hash, id_rol, state, create_at) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"
    # Ejecutar la consulta con los valores del usuario
    _fetch_none(sql, (usuario.name, usuario.email, usuario.password_hash, usuario.id_rol, usuario.state, usuario.create_at))
    # Imprimir datos del usuario para depuración
    print('-------------------------------------------------------------------------')
    print((usuario.name, usuario.email, usuario.password_hash, usuario.id_rol, usuario.state, usuario.create_at))
    print('-------------------------------------------------------------------------21')
    return usuario

# Método para actualizar datos del usuario
def update(usuario: User) -> User:
    # Consulta SQL para actualizar el nombre del usuario basado en su ID
    sql = """UPDATE users SET name = '{}' WHERE ID = '{}'""".format(usuario.name, usuario.id)
    # Ejecutar la consulta
    _fetch_none(sql, None)

# Método login
def login(usuario: User) -> User:
    # Consulta SQL para seleccionar datos del usuario por su email
    sql = "SELECT name, email, password_hash, id_rol, state, create_at FROM users WHERE email = '{}'".format(usuario.email)
    # Ejecutar la consulta
    row = _fetch_one(sql, None)
    # Imprimir datos obtenidos para depuración
    print('---------- DATOS DE CAPA DATO LOGIN')
    print(row)
    # Verificar si se encontró un usuario
    if row != None:
        # Crear un objeto User con los datos obtenidos y verificar la contraseña
        usuario = User(row[0], row[1], User.check_password(row[2], usuario.password_hash), row[3], row[4], row[5])
        print(usuario)
        return usuario  # El usuario se encuentra en la BD_Lab
    else:
        return None  # No hay usuario

# Método para actualizar el estado de un usuario
def update_state(user_data: dict) -> None:
    # Consulta SQL para actualizar el estado del usuario basado en su ID
    sql = "UPDATE users SET state = %s WHERE id = %s"
    # Ejecutar la consulta con los valores del diccionario user_data
    _fetch_none(sql, (user_data['state'], user_data['id']))

# Método para obtener un usuario por su ID
def getById(user_id: int) -> tuple:
    # Consulta SQL para seleccionar un usuario por su ID
    sql = "SELECT id, name, email, state FROM users WHERE id = %s"
    # Ejecutar la consulta
    result = _fetch_one(sql, (user_id,))
    return result

# Método para obtener todos los usuarios
def getAll() -> list:
    # Consulta SQL para seleccionar todos los usuarios
    sql = "SELECT id, name, email, state FROM users"
    # Ejecutar la consulta
    results = _fetch_all(sql, ())  # Pasa una tupla vacía como segundo argumento
    return results

# Método para obtener los datos de un usuario por su email
def id_user(usuario: User) -> tuple:
    # Consulta SQL para seleccionar un usuario por su email
    sql = "SELECT id, name, email, password_hash, id_rol, state, create_at FROM users WHERE email = '{}'".format(usuario.email)
    # Ejecutar la consulta
    row = _fetch_one(sql, None)
    # Verificar si se encontró un usuario
    if row != None:
        return row  # El usuario se encuentra en la BD_Lab
    else:
        return None  # No hay usuario