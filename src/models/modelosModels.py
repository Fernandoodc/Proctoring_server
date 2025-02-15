from flask import flash
from src.database.db_mysql import get_connection
from src.database.models import Modelos as dbModelo, Salidas as dbSalida
from config import settings
import os
from datetime import datetime
from src.funciones import to_dict

class Modelos():
    def __init__(self):
        pass

    @classmethod
    def add_modelo(self, nombre, file, salidas):
        connection = get_connection()
        try:
            filename = file.filename
            file_path = os.path.join(settings.UPLOAD_FOLDER, filename)
            file.save(file_path)
            modelo = dbModelo(descripcion=nombre, path=file_path, fecha=datetime.now(), activo=True)
            connection.add(modelo)
            connection.flush()
            connection.refresh(modelo)
            mapeo = {}
            mapeo["0"] = "Sin Salida"
            for item in salidas.split(","):
                key, value = item.split(":")
                print(key, value)
                if key in mapeo:
                    flash(f"Salida duplicada: {key}", "error")
                    raise ValueError(f"Duplicate key found: {key}")
                mapeo[key] = value
            for key, value in mapeo.items():
                salida = dbSalida(id_modelo=modelo.id_modelo, descripcion=value, etiqueta=key)
                connection.add(salida)
                connection.flush()
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
    def get_modelos_by_ids(self, ids):
        connection = get_connection()
        modelos = connection.query(dbModelo).filter(dbModelo.id_modelo.in_(ids)).all()
        connection.close()
        return modelos
    
    @classmethod
    def get_modelo_by_id_salida(self, id_salida):
        connection = get_connection()
        modelo = connection.query(dbModelo).join(dbSalida).filter(dbSalida.id_salida == id_salida).first()
        connection.close()  
        return modelo
    
    @classmethod
    def get_salidas_by_id_modelo(self, id_modelo):
        connection = get_connection()
        salidas = connection.query(dbSalida).filter(dbSalida.id_modelo == id_modelo).all()
        connection.close()
        return salidas
    
    @classmethod
    def get_all_salidas(self):
        connection = get_connection()
        salidas = connection.query(dbSalida).join(dbModelo).filter(dbModelo.activo == True, dbSalida.etiqueta > 0).all()
        connection.close()
        for index, salida in enumerate(salidas):
            salidas[index] = to_dict(salida)
            print(self.get_modelo_by_id(salida.id_modelo))
            salidas[index]["modelo"] = self.get_modelo_by_id(salida.id_modelo, return_dict=True)
        return salidas