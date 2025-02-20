from src.database.models import Examenes as dbExamenes
from src.database.db_mysql import get_connection

class Examanes():
    def __init__(self):
        pass

    @classmethod
    def add_examen(self, descripcion, fecha, id_usuario):
        connection = get_connection()
        try:
            examen = dbExamenes(descripcion=descripcion, fecha=fecha, id_usuario=id_usuario)
            connection.add(examen)
            connection.commit()
            connection.refresh(examen)
            connection.close()
            return examen.id_examen
        except Exception as e:
            connection.rollback()
            connection.close()
            raise e
        
