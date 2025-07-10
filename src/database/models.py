from sqlalchemy import Column, Integer ,String, Boolean, Date, ForeignKey, DateTime, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from src.database.db_mysql import Base
from sqlalchemy.orm import relationship
from src.database.audit import AuditableMixin


class Usuarios(AuditableMixin, Base):
    __tablename__ = 'Usuarios'
    idUsuario = Column(Integer,primary_key=True,index=True)
    nombre = Column(String(100), nullable=False)
    documento = Column(String(30), nullable=False)
    email = Column(String(100))
    activo = Column(Boolean, nullable=False, default=True)
    username = Column(String(20), unique=True, nullable=False)
    password = Column(String(300), nullable=False)
    id_tipo = Column(Integer, ForeignKey('TipoUsuarios.id_tipo'))

class TipoUsuarios(AuditableMixin, Base):
    __tablename__ = 'TipoUsuarios'
    id_tipo = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(50), nullable=False)

class Modelos(AuditableMixin, Base):
    __tablename__ = 'Modelos'
    id_modelo = Column(Integer, primary_key=True, index=True)
    path = Column(Text, nullable=False)
    descripcion = Column(String(100), nullable=False, unique=True)
    path = Column(String(255), nullable=False)
    fecha = Column(Date, nullable=False)
    salida = Column(String(100), nullable=False)
    activo = Column(Boolean, nullable=False)

class Detecciones(AuditableMixin, Base):
    __tablename__ = 'Detecciones'
    id_deteccion = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey('Usuarios.idUsuario'))
    imagen = Column(LONGTEXT, nullable=False)
    fecha_hora = Column(DateTime, nullable=False)

"""class ImagenesDetecciones(AuditableMixin, Base):
    #tabla temporal y provisoria para guardar las imagenes de detecciones en lo que se resuelve el problema del id de examen actual
    __tablename__ = 'ImagenesDetecciones'
    id_imagen = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey('Usuarios.idUsuario'))
    imagen = Column(LONGTEXT, nullable=False)"""


                                            
    
