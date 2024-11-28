from flask import session
from ..models.User import Plan  
from datetime import datetime
from .connection import _fetch_all,_fecth_lastrow_id,_fetch_none,_fetch_one  #las funciones 

# Obtener todos los planes
def getAll() -> list:
    # Consulta SQL para seleccionar todos los planes
    sql = "SELECT * FROM plans"
    # Ejecutar la consulta
    planes = _fetch_all(sql, None)
    return planes  # Siempre devolver una lista

# Crear un nuevo plan
def create(plan_data) -> None:
    # Consulta SQL para insertar un nuevo plan en la tabla 'plans'
    sql = "INSERT INTO plans (name, description, monthly_price) VALUES (%s, %s, %s)"
    # Ejecutar la consulta con los valores del diccionario plan_data
    _fetch_none(sql, (plan_data['name'], plan_data['description'], plan_data['monthly_price']))

# Actualizar un plan existente
def update(plan_data) -> None:
    # Consulta SQL para actualizar un plan basado en su ID
    sql = "UPDATE plans SET name = %s, description = %s, monthly_price = %s WHERE id = %s"
    # Ejecutar la consulta con los valores del diccionario plan_data
    _fetch_none(sql, (plan_data['name'], plan_data['description'], plan_data['monthly_price'], plan_data['id']))

# Eliminar un plan por su ID
def delete(plan_id) -> None:
    # Consulta SQL para eliminar un plan basado en su ID
    sql = "DELETE FROM plans WHERE id = %s"
    # Ejecutar la consulta con el ID del plan
    _fetch_none(sql, (plan_id,))

# Obtener un plan por su ID
def getById(plan_id: int) -> tuple:
    # Consulta SQL para seleccionar un plan por su ID
    sql = "SELECT id, name, description, monthly_price FROM plans WHERE id = %s"
    # Ejecutar la consulta con el ID del plan
    result = _fetch_one(sql, (plan_id,))
    return result