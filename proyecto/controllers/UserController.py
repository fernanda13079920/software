from ..models.User import User
from ..database import usuario_db
# Usuario de tipo USER que tendrá como resultado de tipo User

# Crear un nuevo usuario
def create(usuario: User) -> User:
    # Falta implementar los métodos de validación, así que hay que ingresar datos correctos, sino genera error
    return usuario_db.create(usuario)

# Actualizar un usuario existente
def update(usuario: User) -> User:
    return usuario_db.update(usuario)

# Iniciar sesión
def login(usuario: User) -> User:
    return usuario_db.login(usuario)

# Actualizar el estado de un usuario
def update_state(user_data: dict) -> None:
    print("Updating user state:", user_data)
    usuario_db.update_state(user_data)

# Obtener un usuario por su ID
def getById(user_id: int) -> dict:
    raw_user = usuario_db.getById(user_id)
    if raw_user:
        print("User found:", raw_user)
        return {
            'id': raw_user[0],
            'name': raw_user[1],
            'email': raw_user[2],
            'state': raw_user[3]
        }
    print("User not found with ID:", user_id)
    return None

# Obtener todos los usuarios
def getAll() -> list:
    raw_users = usuario_db.getAll()
    return [
        {'id': user[0], 'name': user[1], 'email': user[2], 'state': user[3]}
        for user in raw_users
    ]

# Obtener un usuario por su email
def id_user(usuario: User) -> tuple:
    return usuario_db.id_user(usuario)
