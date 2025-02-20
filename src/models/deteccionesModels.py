from src.database.db_mysql import get_connection
from src.database.models import ImagenesDetecciones as dbImagenesDetecciones
from src.database.models import Detecciones as dbDetecciones

class Detecciones():
    def __init__(self):
        pass

    @classmethod
    def add_img_deteccion(self, id_usuario, imagen):
        connection = get_connection()
        try:
            img_deteccion = dbImagenesDetecciones(id_usuario=id_usuario, imagen=imagen)
            connection.add(img_deteccion)
            connection.commit()
            connection.refresh(img_deteccion)
            connection.close()
            return img_deteccion.id_imagen
        except Exception as e:
            connection.rollback()
            connection.close()
            raise e
    
    @classmethod
    def get_img_deteccion(self, id):
        connection = get_connection()
        try:
            img_deteccion = connection.query(dbImagenesDetecciones).filter_by(id_imagen=id).first()
            connection.close()
            return img_deteccion
        except Exception as e:
            connection.close()
            raise e