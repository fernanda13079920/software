from ..models.User import Subscription
from ..database import suscripcion



def create(subs) -> None:
    return suscripcion.create(subs)

def getById(user_id: int) -> dict:
    subs = suscripcion.getById(user_id)
    if subs:
        return {'user': subs[0], 'plan': subs[1], 'state': subs[2], 'fecha': subs[3], 'monthly_price':subs[4]}
    return None

