import traceback

# Database
from src.database.db_mysql import get_connection
# Logger
from src.utils.Logger import Logger
# Models
from src.models.usersModels import User
from src.database.models import Usuarios as dbUSer

class AuthService():

    @classmethod
    def login_user(cls, user):
        try:
            connection = get_connection()
            authenticated_user = None
            row = connection.query(dbUSer).filter(dbUSer.username == user.username).first()
            if row != None:
                if row.activo == False:
                    return None
                check_password = User.check_password(row.password, user.password)
                authenticated_user = User(row.idUsuario, row.username, check_password, row.nombre, row.id_tipo)
            connection.close()
            return authenticated_user
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())

class Permisos():
    USUARIOS = ('usuarios', 'Usuarios')
    PEDIDOS = ('pedidos', 'Pedidos')
    MENU = ('menu', "Menu y Acompañamientos")
    COCINA = ('cocina', 'Cocina')
    CLIENTES = ('clientes', "Clientes")
    CAJA = ('caja', 'Caja')
    PROVEEDORES = ('proveedores', 'Proveedores')
    FACTURAS = ('facturas', 'Facturas')
    REPORTES = ('reportes', "Reportes")
    INVENTARIO = ('inventario', "Inventario")
    INSUMOS = ("insumos", "Insumos")

permisos = Permisos()
