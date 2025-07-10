from src.database.db_mysql import get_connection
from src.database.models import Detecciones as dbDetecciones
from datetime import datetime
import cv2
from config import settings
import uuid 

class Detecciones():
    def __init__(self):
        pass

    @classmethod
    def add_img_deteccion(self, id_usuario, imagen):
        connection = get_connection()
        try:
            fecha = datetime.now()
            unique_id = uuid.uuid4()
            path = f"{settings.DETENCIONES_FOLDER}deteccion-{unique_id}.jpg"
            print(path)
            cv2.imwrite(path, imagen)
            partesDst = path.split("/")
            dst ="/" + "/".join(partesDst[1:])
            img_detec = dbDetecciones(id_usuario=id_usuario, imagen=dst, fecha_hora=fecha)
            connection.add(img_detec)
            connection.commit()
            connection.refresh(img_detec)
            connection.close()
            return img_detec.id_deteccion
        except Exception as e:
            print(e)
            connection.rollback()
            connection.close()
            raise e

    @classmethod
    def get_img_deteccion(self, id):
        connection = get_connection()
        try:
            img_deteccion = connection.query(dbDetecciones).filter(dbDetecciones.id_deteccion==id).first()
            connection.close()
            return img_deteccion
        except Exception as e:
            connection.close()
            raise e