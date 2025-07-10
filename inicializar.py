from src.database import models as dbModels
from src.database.db_mysql import engine, get_connection
from src.database.models import TipoUsuarios, Usuarios

dbModels.Base.metadata.create_all(bind=engine)
connection = get_connection()

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
connection.close()