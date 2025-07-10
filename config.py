from types import SimpleNamespace
from decouple import config
import os
from dotenv import load_dotenv
load_dotenv()

class Config():
    SECRET_KEY = config('SECRET_KEY')


class Settings:
    PROJECT_TITLE: str = ""
    PROJECT_VERSION: str = "0.1"
    DATABASE_URL = "mysql+mysqlconnector://admin:admin@localhost:3310/tesis"
    ALGORITHM = "HS256"
    HASH = "pbkdf2:sha256"
    UPLOAD_FOLDER = "modelos/"
    DETENCIONES_FOLDER = "src/static/uploads/detecciones/"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    KEY_TOKEN: str = "access-token"
    VIDA_TOKEN : int =  6  #Horas de vida del token de sesion
settings = Settings()

class DevelopmentConfig(Config):
    DEBUG = True



config = {
    'development': DevelopmentConfig
}


