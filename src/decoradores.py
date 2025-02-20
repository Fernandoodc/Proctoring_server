from functools import wraps
from flask import session
from flask_login import current_user
from flask_socketio import disconnect

def roles_required(*role_numbers: int):
    def wrapper(f):
        @wraps(f)   
        def wrap(*args, **kwargs):
            for r in role_numbers:
                if r == session['_tipo_usuario'] or 1 == session['_tipo_usuario']: #1 es el rol de Administrador
                    return f(*args, **kwargs)
            return "You do not have the role to perform this operation", 401
        return wrap
    return wrapper

# Decorador para verificar si el usuario está autenticado
def authenticated_only(f):
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped