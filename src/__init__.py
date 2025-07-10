from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO
from config import settings
from tensorflow.keras.models import load_model
from src.database.db_mysql import get_connection
from src.database.models import Modelos as dbModelo
from src.database import models as dbModels
from src.database.db_mysql import engine
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER
app.config['DETENCIONES_FOLDER'] = settings.DETENCIONES_FOLDER
dbModels.Base.metadata.create_all(bind=engine)



socketio = SocketIO(app, cors_allowed_origins="*")
login_manager_main = LoginManager(app)

CONECTADOS = {}
connection = get_connection()
MODELS = connection.query(dbModelo).filter(dbModelo.activo == True).all()
connection.close()

loaded_models = {}
for modelo in MODELS:
    loaded_models[modelo.id_modelo] = {
        "modelo": load_model(modelo.path),
        "nombre": modelo.descripcion
}
print(loaded_models, "MODELOS CARGADOS")


active_connections = {}
HEARTBEAT_TIMEOUT = 10  # Tiempo de espera para el latido (en segundos)

detections = []  # Lista para almacenar las notificaciones de detección

MODELOS_SELECCIONADOS = [] # Lista para almacenar los modelos seleccionados por el usuario