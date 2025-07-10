from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from src.database.db_mysql import get_connection
from src.database.models import Usuarios as dbUser, TipoUsuarios as dbTipoUsuarios
from config import settings
class User(UserMixin):
    def __init__(self, id, username, password, fullname, id_tipo = None) -> None:
        self.id = id
        self.username = username
        self.password = password
        self.fullname = fullname
        self.tipo_usuario = self.get_tipo_by_id(id)
    
    @classmethod
    def get_by_id(self, id):
        try:
            connection = get_connection()
            row = connection.query(dbUser).filter(dbUser.idUsuario == id).first()
            connection.close()
            if row != None:
                return User(row.idUsuario, row.username, row.password, row.nombre)
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
    
    @classmethod
    def get_by_username(self, username):
        print(username)
        try:
            connection = get_connection()
            row = connection.query(dbUser).filter(dbUser.username == username).first()
            connection.close()
            if row != None:
                return User(row.idUsuario, row.username, None, row.nombre)
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
         
    @classmethod
    def get_full_by_id(self, idUsuario):
        #parecido al de arriba solo que devuelve toda la fila del usuario, retorna directo el objeto de sqlalchemy
        connection = get_connection()
        usuario = connection.query(dbUser).filter(dbUser.idUsuario == idUsuario).first()
        connection.close()
        return usuario

    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)
    
    @classmethod
    def current_user_id(self):
        return session["_user_id"]
    
    @classmethod
    def get_tipos_usuarios(self):
        connection = get_connection()
        tipos = connection.query(dbTipoUsuarios).all()
        connection.close()
        return tipos

    @classmethod
    def get_tipo_by_id(self, id):
        connection = get_connection()
        tipo = connection.query(dbUser).filter(dbUser.idUsuario == id).first()
        connection.close()
        if tipo == None:
            return None
        return tipo.id_tipo

    @classmethod
    def get_users(self):
        connection = get_connection()
        usuarios = connection.query(dbUser).all()
        connection.close()
        return usuarios

    @classmethod
    def add_user(self, username, password, nombre, documento, tipo_usuario):
        connection = get_connection()
        newUser = dbUser(
            username = username,
            password = generate_password_hash(password, method=settings.HASH),
            nombre = nombre,
            documento = documento,
            id_tipo = tipo_usuario,
            activo = True
        )
        connection.add(newUser)
        connection.commit()
        connection.refresh(newUser)
        connection.close()
        return newUser.idUsuario
    
    @classmethod
    def update_user(self, idUsuario, nombre, documento, tipo_usuario):
        connection = get_connection()
        usuario = connection.query(dbUser).filter(dbUser.idUsuario == idUsuario).first()
        usuario.nombre = nombre
        usuario.documento = documento
        usuario.id_tipo = tipo_usuario
        connection.commit()
        connection.close()
    
    @classmethod
    def set_new_password_by_id(self, idUsuario, password):
        connection = get_connection()
        usuario = connection.query(dbUser).filter(dbUser.idUsuario == idUsuario).first()
        usuario.password = generate_password_hash(password, method=settings.HASH)
        connection.commit()
        connection.refresh(usuario)
        connection.close()
    
    @classmethod
    def set_activo_by_id(self, idUsuario):
        connection = get_connection()
        usuario = connection.query(dbUser).filter(dbUser.idUsuario == idUsuario).first()
        usuario.activo = True
        connection.commit()
        connection.close()
    
    @classmethod
    def set_inactivo_by_id(self, idUsuario):
        connection = get_connection()
        usuario = connection.query(dbUser).filter(dbUser.idUsuario == idUsuario).first()
        usuario.activo = False
        connection.commit()
        connection.close()
