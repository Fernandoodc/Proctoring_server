from flask import Blueprint, redirect, session

main = Blueprint('index_blueprint', __name__)

@main.route('/')
def index():
    tipo_usuario = session.get("_tipo_usuario")
    
    if tipo_usuario == 1 or tipo_usuario == 2:
        return redirect("/admin")
    elif tipo_usuario == 3:
        return redirect("/stream")
    else:
        return redirect("/auth")  # Redirigir a la página de inicio de sesión si el tipo de usuario no está definido