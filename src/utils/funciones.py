import datetime
from ..services.AuthService import permisos as Permisos
def to_dict(object, formatDateTime = False):
    def format_datetime(value):
        if isinstance(value, datetime.date):
            return value.strftime('%Y-%m-%d')
        elif isinstance(value, datetime.time):
            return value.strftime('%H:%M:%S')
        return value
    #Convierte los objetos de SQLalchemy al un diccionario que flask puede retornar
    # Convierte el objeto SQLAlchemy a un diccionario
    pedido_dict = object.__dict__.copy()
    # Remueve atributos especiales de SQLAlchemy}
    pedido_dict.pop('_sa_instance_state', None)
    if formatDateTime == True:
        # Formatear fechas y horas
        for key, value in pedido_dict.items():
            pedido_dict[key] = format_datetime(value)
    return pedido_dict

def get_list_permisos():
    listPermisos = []
    for attr_name in dir(Permisos):
        # Filtrar los atributos que no son métodos especiales ni atributos especiales
        if not attr_name.startswith("__"):
            attr_value = getattr(Permisos, attr_name)
            if isinstance(attr_value, tuple):
                aux = (attr_value[0], attr_value[1])
                listPermisos.append(aux)
    return listPermisos