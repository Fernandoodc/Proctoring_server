from flask_socketio import SocketIO, disconnect, emit, Namespace
from src.decoradores import authenticated_only
from flask_login import current_user
from flask import request
from index import socketio, app, loaded_models
import base64
import cv2
import os
import numpy as np
import time
import threading 
active_connections = {}
HEARTBEAT_TIMEOUT = 10  # Tiempo de espera para el latido (en segundos)

detections = []  # Lista para almacenar las notificaciones de detección

@socketio.on('connect')
def handle_connect():
    active_connections[request.sid] = time.time()  # Guardar la hora de conexión
    id_user = current_user.id
    print('Un cliente se ha conectado : ' + request.sid + " ID: " + str(id_user))

@socketio.on('disconnect')
def handle_disconnect():
    active_connections.pop(request.sid, None)  # Eliminar del registro
    print('Un cliente se ha desconectado: ' + request.sid)
    file = f'frame{request.sid}.jpg'
    if os.path.exists(file):
        os.remove(file)

@socketio.on('heartbeat')
@authenticated_only
def handle_heartbeat():
    active_connections[request.sid] = time.time()  # Actualizar la hora del último latido

def check_heartbeats():
    while True:
        time.sleep(1)  # Esperar un segundo entre verificaciones
        current_time = time.time()
        for sid in list(active_connections.keys()):
            if current_time - active_connections[sid] > HEARTBEAT_TIMEOUT:
                print(f'Desconectando cliente inactivo: {sid}')
                with app.app_context():
                    disconnect(sid)  # Desconectar el cliente

def process_frame(frame, sid):
    """Procesar el frame recibido y realizar la predicción con múltiples modelos."""
    try:
        # Convertir el frame a una imagen de OpenCV
        np_arr = np.frombuffer(frame, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Redimensionar la imagen al tamaño esperado por los modelos
        img_resized = cv2.resize(img, (281, 500))  # (ancho, alto)
        img_normalized = img_resized.astype(float) / 255.0
        img_array = np.expand_dims(img_normalized, axis=0)

        results = {}
        threads = []
        results_lock = threading.Lock()

        def predict_with_model(model_name, model):
            """Función para predecir con un modelo específico."""
            prediction = model.predict(img_array)
            confidence = prediction[0][np.argmax(prediction[0])]
            detected = np.argmax(prediction[0]) == 0
            with results_lock:
                results[model_name] = (detected, confidence)

        # Crear y ejecutar un hilo por modelo
        for model_name, model in loaded_models.items():
            thread = threading.Thread(target=predict_with_model, args=(model_name, model))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Seleccionar el mejor resultado
        best_model = None
        highest_confidence = 0
        for model_name, (detected, confidence) in results.items():
            if detected and confidence > highest_confidence:
                best_model = model_name
                highest_confidence = confidence

        if best_model:
            print(f"Detectado: {best_model} con confianza de {highest_confidence:.2f}")
            detection_message = {
                'sid': sid,
                'modelo': best_model,
                'confianza': float(highest_confidence)
            }
            detections.append(detection_message)  # Guardar la detección
            socketio.emit('new_detection', detection_message, namespace='/admin')
        else:
            print("No se detectó nada")

        """socketio.emit('prediction_result', {
            'sid': sid,
            'resultado': best_model if best_model else "No Detectado",
            'confianza': highest_confidence if best_model else 0
        })"""
    except Exception as e:
        print(f"Error procesando el frame: {str(e)}")

@socketio.on('video_frame')
@authenticated_only
def handle_video_frame(data):
    """Procesar los frames recibidos vía WebSocket."""
    try:
        # El frame llega como base64, lo decodificamos
        image_data = data.split(",")[1]  # Obtener solo los datos, sin la cabecera base64
        frame = base64.b64decode(image_data)

        # Crear un hilo para procesar el frame
        threading.Thread(target=process_frame, args=(frame, request.sid)).start()
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