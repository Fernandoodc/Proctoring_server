from flask import Flask, render_template, request, redirect
from src.routes import AuthRoutes, StreamRoutes, AdminRoutes
from flask_login import LoginManager, current_user
from src.database import models as dbModels
from src.database.db_mysql import engine
from src.models.usersModels import User
from src.decoradores import authenticated_only
import base64
import os
import numpy as np
from flask_socketio import SocketIO, emit, Namespace
import time
import threading
from src.funciones import process_frame, check_heartbeats
from src import *
# Cargar múltiples modelos

dbModels.Base.metadata.create_all(bind=engine)


@login_manager_main.user_loader
def load_user(id):
    return User.get_by_id(id)

def status_401(error):
    return redirect("/auth/")

app.register_error_handler(401, status_401)
app.register_blueprint(AuthRoutes.main, url_prefix='/auth')
app.register_blueprint(StreamRoutes.main, url_prefix='/stream')
app.register_blueprint(AdminRoutes.main, url_prefix='/admin')


@socketio.on('connect')
@authenticated_only
def handle_connect():
    active_connections[request.sid] = time.time()  # Guardar la hora de conexión
    id_user = current_user.id
    print('Un cliente se ha conectado : ' + request.sid + " ID: " + str(id_user))
    CONECTADOS[request.sid] = {
        "id": id_user,
        "nombre": User.get_by_id(id_user).fullname
    }
    print(CONECTADOS)

@socketio.on('disconnect')
def handle_disconnect():
    active_connections.pop(request.sid, None)  # Eliminar del registro
    print('Un cliente se ha desconectado: ' + request.sid)
    CONECTADOS.pop(request.sid, None)  # Eliminar del registro
    file = f'frame{request.sid}.jpg'
    if os.path.exists(file):
        os.remove(file)

@socketio.on('heartbeat')
@authenticated_only
def handle_heartbeat():
    active_connections[request.sid] = time.time()  # Actualizar la hora del último latido




@socketio.on('video_frame')
@authenticated_only
def handle_video_frame(data):
    """Procesar los frames recibidos vía WebSocket."""
    try:
        # El frame llega como base64, lo decodificamos
        image_data = data.split(",")[1]  # Obtener solo los datos, sin la cabecera base64
        frame = base64.b64decode(image_data)

        # Crear un hilo para procesar el frame
        threading.Thread(target=process_frame, args=(frame, request.sid), daemon=True).start()
    except Exception as e:
        print(f"Error procesando el video_frame: {str(e)}")

# Iniciar el hilo para verificar los latidos
threading.Thread(target=check_heartbeats, daemon=True).start()

class AdminNamespace(Namespace):
    def on_connect(self):
        print('Un administrador se ha conectado')
        emit('detections', detections)

    def on_disconnect(self):
        print('Un administrador se ha desconectado')

socketio.on_namespace(AdminNamespace('/admin'))

if __name__ == '__main__':
    #load_models()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, host='0.0.0.0')