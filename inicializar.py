from src.database import models as dbModels
from src.database.db_mysql import engine, get_connection
from src.database.models import TipoUsuarios, Usuarios
from werkzeug.security import generate_password_hash
from config import settings

dbModels.Base.metadata.create_all(bind=engine)
connection = get_connection()

try:
    #crear tipos de usuarios
    print("Inicializando tipos de usuarios...")
    TipoDeUsuarios = [
        {
            "id":1,
            "descripcion": "Administrador"
        },
        {
            "id":2,
            "descripcion":"Docente"
        },
        {
            "id":3,
            "descripcion":"Estudiante"
        }
    ]
    for tipo in TipoDeUsuarios:
        connection = get_connection()
        tipoUser = TipoUsuarios(id_tipo=tipo["id"], descripcion=tipo["descripcion"])
        connection.add(tipoUser)
        connection.commit()
    print("Tipos de usuarios creados exitosamente.")    
    #crear usuario administrador
    print("Inicializando usuario administrador...")
    usuarioAdmin = Usuarios(
        username = "admin",
            password = generate_password_hash("admin", method=settings.HASH),
            nombre = "Administrador",
            documento = "12345678",
            id_tipo = 1,  # Asignar el tipo de usuario administrador
            activo = True
        )
    connection.add(usuarioAdmin)
    print("Usuario administrador creado exitosamente. \nUsuario: admin \nContraseña: admin")
    connection.commit()
    print("Base de datos inicializada correctamente.")
except Exception as e:
    print(f"Error al inicializar la base de datos: {e}")
    connection.rollback()  # Deshacer cambios en caso de error
finally:
    # Cerrar la conexión
    connection.close()