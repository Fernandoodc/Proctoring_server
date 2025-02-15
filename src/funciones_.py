from flask_socketio import disconnect
import time
import multiprocessing
import cv2
import numpy as np
from datetime import datetime
from src import detections, active_connections, HEARTBEAT_TIMEOUT, socketio, app, MODELOS_SELECCIONADOS, CONECTADOS

# Variable global para los modelos compartidos
shared_models = {}


def to_dict(object, formatDateTime=False):
    """Convierte objetos de SQLAlchemy a un diccionario."""
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

def load_models():
    """Carga los modelos una sola vez en memoria compartida."""
    global shared_models
    print("Cargando modelos en memoria compartida...")
    manager = multiprocessing.Manager()
    shared_models = manager.dict()

    for model_key in MODELOS_SELECCIONADOS:
        modelo_info = MODELOS_SELECCIONADOS[model_key]
        shared_models[model_key] = {
            'nombre': modelo_info['nombre'],
            'modelo': modelo_info['modelo']  # Modelo ya cargado en memoria
        }
    print("Modelos cargados en memoria compartida.")
    print(shared_models)

def predict_with_model(model_name, model, img_array, result_queue):
    """Ejecuta la predicción con el modelo compartido."""
    prediction = model.predict(img_array)
    confidence = prediction[0][np.argmax(prediction[0])]
    detected = np.argmax(prediction[0]) == 0
    result_queue.put((model_name, detected, confidence))

def process_frame(frame, sid):
    """Procesa el fotograma recibido y realiza la predicción con modelos compartidos."""
    print(shared_models)
    if not shared_models:
        print("No hay modelos cargados.")
        return 0

    try:
        np_arr = np.frombuffer(frame, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        img_resized = cv2.resize(img, (225, 400))
        img_normalized = img_resized.astype(float) / 255.0
        img_array = np.expand_dims(img_normalized, axis=0)

        result_queue = multiprocessing.Queue()
        processes = []

        for model_key in shared_models.keys():
            model_info = shared_models[model_key]
            model_name = model_info['nombre']
            model = model_info['modelo']

            process = multiprocessing.Process(
                target=predict_with_model,
                args=(model_name, model, img_array, result_queue)
            )
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

        results = {}
        while not result_queue.empty():
            model_name, detected, confidence = result_queue.get()
            results[model_name] = (detected, confidence)

        best_model = None
        highest_confidence = 0
        for model_name, (detected, confidence) in results.items():
            if detected and confidence > highest_confidence:
                best_model = model_name
                highest_confidence = confidence

        if not best_model:
            print("No se detectó nada")
            detection_message = {
                'sid': CONECTADOS[sid]['nombre'],
                'modelo': "No Detectado",
                'confianza': 0
            }
            detections.append(detection_message)
            socketio.emit('new_detection', detection_message, namespace='/admin')
        else:
            print(f"Detectado: {best_model} con confianza de {highest_confidence:.2f}")

    except Exception as e:
        print(f"Error procesando el fotograma: {str(e)}")

def check_heartbeats():
    """Verifica que los clientes sigan enviando señales de vida."""
    while True:
        time.sleep(1)
        current_time = time.time()
        for sid in list(active_connections.keys()):
            if current_time - active_connections[sid] > HEARTBEAT_TIMEOUT:
                print(f'Desconectando cliente inactivo: {sid}')
                with app.app_context():
                    disconnect(sid)
