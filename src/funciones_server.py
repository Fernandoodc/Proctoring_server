from flask_socketio import disconnect
import time
import threading
import cv2
import numpy as np
from datetime import datetime
import requests
import json
from src import detections, active_connections, HEARTBEAT_TIMEOUT, socketio, app, CONECTADOS

# Configuración del servidor TensorFlow Serving
TF_SERVING_URL = "http://localhost:8501/v1/models/facebook:predict"  # Cambia "facebook" si usaste otro nombre

def to_dict(object, formatDateTime=False):
    """Convierte los objetos de SQLAlchemy a un diccionario que Flask puede retornar."""
    def format_datetime(value):
        if isinstance(value, datetime.date):
            return value.strftime('%Y-%m-%d')
        elif isinstance(value, datetime.time):
            return value.strftime('%H:%M:%S')
        return value

    object_dict = object.__dict__.copy()
    object_dict.pop('_sa_instance_state', None)
    if formatDateTime:
        for key, value in object_dict.items():
            object_dict[key] = format_datetime(value)
    return object_dict

def process_frame(frame, sid):
    """Procesar el frame recibido y realizar la predicción con el servidor de TensorFlow Serving."""
    try:
        # Convertir el frame a una imagen de OpenCV
        np_arr = np.frombuffer(frame, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Redimensionar la imagen al tamaño esperado por el modelo
        img_resized = cv2.resize(img, (281, 500))  # (ancho, alto)
        img_normalized = img_resized.astype(float) / 255.0
        img_array = np.expand_dims(img_normalized, axis=0)

        # Preparar los datos para la solicitud
        data = {
            "instances": img_array.tolist()  # Convertir a lista para JSON
        }

        # Medir el tiempo antes de enviar la solicitud
        start_time = time.time()

        # Enviar la solicitud al servidor TensorFlow Serving
        response = requests.post(TF_SERVING_URL, data=json.dumps(data))
        response.raise_for_status()  # Verificar si hubo errores en la solicitud

        # Medir el tiempo después de recibir la respuesta
        end_time = time.time()
        elapsed_time = end_time - start_time  # Calcular el tiempo transcurrido

        # Obtener la predicción
        prediction = response.json()["predictions"][0]
        confidence = prediction[np.argmax(prediction)]
        detected = np.argmax(prediction) == 0

        # Determinar el resultado
        if detected:
            result = "Detectado"
        else:
            result = "No Detectado"

        # Mostrar el resultado
        print(f"Resultado: {result}, Confianza: {confidence:.2f}, Tiempo: {elapsed_time:.4f} segundos")

        # Enviar el resultado a través de SocketIO
        detection_message = {
            'sid': CONECTADOS[sid]['nombre'],
            'modelo': result,
            'confianza': float(confidence),
            'tiempo': elapsed_time
        }
        detections.append(detection_message)  # Guardar la detección
        socketio.emit('new_detection', detection_message, namespace='/admin')

    except Exception as e:
        print(f"Error procesando el frame: {str(e)}")
        detection_message = {
            'sid': CONECTADOS[sid]['nombre'],
            'modelo': "Error",
            'confianza': 0,
            'tiempo': 0
        }
        socketio.emit('new_detection', detection_message, namespace='/admin')

def check_heartbeats():
    """Verificar que los clientes estén enviando latidos.
    Si un cliente no envía un latido en un tiempo determinado, se desconectará.
    """
    while True:
        time.sleep(1)  # Esperar un segundo entre verificaciones
        current_time = time.time()
        for sid in list(active_connections.keys()):
            if current_time - active_connections[sid] > HEARTBEAT_TIMEOUT:
                print(f'Desconectando cliente inactivo: {sid}')
                with app.app_context():
                    disconnect(sid)  # Desconectar el cliente