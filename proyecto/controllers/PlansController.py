from ..models.User import Plan
from ..database import plans

# Obtener todos los planes
def getAll() -> list:
    raw_plans = plans.getAll()  # Llama a la función getAll del módulo plans
    # Convierte la lista de tuplas en una lista de diccionarios
    plans_list = [{'id': p[0], 'name': p[1], 'description': p[2], 'monthly_price': p[3]} for p in raw_plans]
    return plans_list

# Crear un nuevo plan
def create(plan_data) -> None:
    return plans.create(plan_data)  # Llama a la función create del módulo plans con los datos del plan

# Actualizar un plan existente
def update(plan_data) -> None:
    return plans.update(plan_data)  # Llama a la función update del módulo plans con los datos del plan

# Eliminar un plan por su ID
def delete(plan_id) -> None:
    return plans.delete(plan_id)  # Llama a la función delete del módulo plans con el ID del plan

# Obtener un plan por su ID
def getById(plan_id: int) -> dict:
    raw_plan = plans.getById(plan_id)  # Llama a la función getById del módulo plans con el ID del plan
    if raw_plan:
        # Convierte la tupla en un diccionario
        return {'id': raw_plan[0], 'name': raw_plan[1], 'description': raw_plan[2], 'monthly_price': raw_plan[3]}
    return None  # Devuelve None si el plan no se encuentra
