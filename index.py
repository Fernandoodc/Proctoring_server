from flask import request, redirect, url_for
from src.routes import AuthRoutes, StreamRoutes, AdminRoutes, UsuariosRoutes, IndexRoutes
from flask_login import current_user
from datetime import datetime
from src.models.usersModels import User
from src.decoradores import authenticated_only
import base64
import numpy as np
from flask_socketio import emit, Namespace
import time
import threading
from src.utils.funciones import process_frame, check_heartbeats
from src import socketio, app, login_manager_main, active_connections, CONECTADOS, detections
# Cargar múltiples modelos


@login_manager_main.user_loader
def load_user(id):
    return User.get_by_id(id)

def status_401(error):
    return redirect("/auth/")

# Rutas
app.register_error_handler(401, status_401)
app.register_blueprint(IndexRoutes.main, url_prefix='/')
app.register_blueprint(AuthRoutes.main, url_prefix='/auth')
app.register_blueprint(StreamRoutes.main, url_prefix='/stream')
app.register_blueprint(AdminRoutes.main, url_prefix='/admin')
app.register_blueprint(UsuariosRoutes.main, url_prefix='/usuarios')

# Manejar la conexión de un cliente
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
    socketio.emit('connecteds', CONECTADOS, namespace='/admin')
# Manejar la desconexión de un cliente
@socketio.on('disconnect')
def handle_disconnect():
    active_connections.pop(request.sid, None)  # Eliminar del registro
    print('Un cliente se ha desconectado: ' + request.sid)
    CONECTADOS.pop(request.sid, None)  # Eliminar del registro
    #file = f'frame{request.sid}.jpg'
    #if os.path.exists(file):
    #   os.remove(file)
    socketio.emit('connecteds', CONECTADOS, namespace='/admin')

# Manejar los latidos de un cliente, para verificar que esté conectado
@socketio.on('heartbeat')
@authenticated_only
def handle_heartbeat():
    active_connections[request.sid] = time.time()  # Actualizar la hora del último latido



# Manejar los frames de video recibidos
@socketio.on('video_frame')
@authenticated_only
def handle_video_frame(data):
    """Procesar los frames recibidos vía WebSocket."""
    try:
        # El frame llega como base64, es decodificado
        image_data = data.split(",")[1]
        frame = base64.b64decode(image_data)

        # Si ya de realizó una deteccion en un usuario, se espera X segundos para volver a realizar otra
        if 'hora_ultima_det' in CONECTADOS[request.sid]:
            now = datetime.now()
            diff = now - CONECTADOS[request.sid]['hora_ultima_det']
            if diff.total_seconds() < 1:
                return
        # Crear un hilo para procesar el frame
        threading.Thread(target=process_frame, args=(frame, request.sid), daemon=True).start()
    except Exception as e:
        print(f"Error procesando el video_frame: {str(e)}")

# Iniciar el hilo para verificar los latidos
threading.Thread(target=check_heartbeats, daemon=True).start()


class AdminNamespace(Namespace):
    # Manejar la conexión de un administrador
    def on_connect(self):
        print('Un administrador se ha conectado')
        emit('connecteds', CONECTADOS)
        emit('detections', detections)

    def on_disconnect(self):
        print('Un administrador se ha desconectado')

socketio.on_namespace(AdminNamespace('/admin'))

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, host='0.0.0.0', ssl_context='adhoc')