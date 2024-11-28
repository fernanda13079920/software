from flask import session
from ..models.User import Subscription 
from datetime import datetime
from .connection import _fetch_all,_fecth_lastrow_id,_fetch_none,_fetch_one  #las funciones 

# Suscripciones

# Crear una nueva suscripción
def create(subs) -> None:
    # Consulta SQL para insertar una nueva suscripción en la tabla 'subscriptions'
    sql = "INSERT INTO subscriptions (user_id, plan_id, start_date, status) VALUES (%s, %s, %s, %s)"
    # Ejecutar la consulta con los valores del diccionario subs
    _fetch_none(sql, (subs['id_user'], subs['id_plan'], subs['start_date'], subs['state']))

# Obtener una suscripción por el ID del usuario
def getById(user_id: int) -> tuple:
    # Consulta SQL para seleccionar los detalles de la suscripción de un usuario
    sql = """
    SELECT 
        users.name AS user_name, 
        plans.name AS plan_name, 
        subscriptions.status AS plan_status, 
        subscriptions.start_date, 
        plans.monthly_price 
    FROM 
        users 
    JOIN 
        subscriptions ON users.id = subscriptions.user_id 
    JOIN 
        plans ON subscriptions.plan_id = plans.id 
    WHERE 
        users.id = %s;
    """
    # Ejecutar la consulta con el ID del usuario
    result = _fetch_one(sql, (user_id,))
    return result



