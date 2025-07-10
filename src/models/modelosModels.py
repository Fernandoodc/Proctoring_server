from flask import flash
from src.database.db_mysql import get_connection
from src.database.models import Modelos as dbModelo
from config import settings
import os
from datetime import datetime
from src.utils.funciones import to_dict

class Modelos():
    def __init__(self):
        pass

    @classmethod
    def add_modelo(self, nombre, file, salida):
        connection = get_connection()
        try:
            filename = file.filename
            file_path = os.path.join(settings.UPLOAD_FOLDER, filename)
            file.save(file_path)
            #modelo = dbModelo(descripcion=nombre, path=file_path, salida=salida ,fecha=datetime.now(), activo=True)
            modelo = dbModelo(descripcion=nombre, path=file_path, salida=salida ,fecha=datetime.now(), activo=True)
            connection.add(modelo)
            connection.flush()
            connection.refresh(modelo)
            connection.commit()
            connection.close()
            flash("Modelo agregado correctamente", "success")
        except ValueError as e:
            connection.rollback()
            connection.close()
            raise e
        except Exception as e: 
            connection.rollback()
            connection.close()
            flash("Error al agregar el modelo", "error")
            raise e

    @classmethod
    def desactivar_modelo(self, id_modelo):
        connection = get_connection()
        try:
            modelo = connection.query(dbModelo).filter(dbModelo.id_modelo == id_modelo).first()
            modelo.activo = False
            connection.commit()
            connection.close()
            flash("Modelo desactivado correctamente", "success")
        except Exception as e:
            connection.rollback()
            connection.close()
            flash("Error al desactivar el modelo", "error")
            raise e
    
    @classmethod
    def activar_modelo(self, id_modelo):
        connection = get_connection()
        try:
            modelo = connection.query(dbModelo).filter(dbModelo.id_modelo == id_modelo).first()
            modelo.activo = True
            connection.commit()
            connection.close()
            flash("Modelo activado correctamente", "success")
        except Exception as e:
            connection.rollback()
            connection.close()
            flash("Error al activar el modelo", "error")
            raise
    
    @classmethod
    def get_modelo_by_id(self, id_modelo, return_dict = False):
        connection = get_connection()
        modelo = connection.query(dbModelo).filter(dbModelo.id_modelo == id_modelo).first()
        connection.close()
        if return_dict == True:
            return to_dict(modelo)
        return modelo

    @classmethod
    def get_modelos(self):
        connection = get_connection()
        modelos = connection.query(dbModelo).filter(dbModelo.activo == True).all()
        connection.close()
        return modelos
    
    @classmethod
    def get_all_modelos(self):
        #Trae todos los modelos, activos e inactivos
        connection = get_connection()
        modelos = connection.query(dbModelo).all()
        connection.close()
        return modelos

    @classmethod
    def get_modelos_by_ids(self, ids):
        connection = get_connection()
        modelos = connection.query(dbModelo).filter(dbModelo.id_modelo.in_(ids)).all()
        connection.close()
        return modelos
    