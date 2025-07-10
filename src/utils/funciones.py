from flask_socketio import disconnect
from src.models.deteccionesModels import Detecciones
import time
import threading
import cv2
import numpy as np
from datetime import datetime
from src import loaded_models, detections, active_connections, HEARTBEAT_TIMEOUT, socketio, app, MODELOS_SELECCIONADOS, CONECTADOS
def to_dict(object, formatDateTime = False):
    def format_datetime(value):
        if isinstance(value, datetime.date):
            return value.strftime('%Y-%m-%d')
        elif isinstance(value, datetime.time):
            return value.strftime('%H:%M:%S')
        return value
    # Convierte el objeto SQLAlchemy a un diccionario
    object_dict = object.__dict__.copy()
    # Remueve atributos especiales de SQLAlchemy}
    object_dict.pop('_sa_instance_state', None)
    if formatDateTime == True:
        # Formatear fechas y horas
        for key, value in object_dict.items():
            object_dict[key] = format_datetime(value)
    return object_dict



def process_frame(frame, sid):
    """Procesa el frame recibido y realizar la predicción con múltiples modelos."""
    print(MODELOS_SELECCIONADOS)
    if MODELOS_SELECCIONADOS == []:
        return 0
    try:
        # Convertir el frame a una imagen de OpenCV
        np_arr = np.frombuffer(frame, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)


        # Redimensionar la imagen al tamaño esperado por los modelos y normalizar los valores de los pixeles
        img_resized = cv2.resize(img, (225, 400))
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
        for model in loaded_models:
            #verifica si está en la lista de modelos seleccionados
            if model in MODELOS_SELECCIONADOS:
                model_name = loaded_models[model]['nombre']
                model = loaded_models[model]['modelo']
                #realiza las predicciones en hilos
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
                if confidence > 0.95:
                    best_model = model_name
                    highest_confidence = confidence
                print(f"----Modelo: {model_name}, Confianza: {confidence:.2f}")
        if not best_model:
            print("No se detectó nada")
            #CONECTADOS[sid]['hora_ultima_det'] = datetime.now()
            id_deteccion = Detecciones.add_img_deteccion(CONECTADOS[sid]['id'], img)
            detection_message = {
                'id_usuario': CONECTADOS[sid]['id'],
                'usuario': CONECTADOS[sid]['nombre'],
                'mensaje': "Actividad Sospechosa",
                'id_imagen': id_deteccion
            }
            detections.append(detection_message)  # Guardar la detección
            socketio.emit('new_detection', detection_message, namespace='/admin')
        else:
            print(f"Detectado: {best_model} con confianza de {highest_confidence:.2f}")
    except Exception as e:
        print(f"Error procesando el frame: {str(e)}")

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