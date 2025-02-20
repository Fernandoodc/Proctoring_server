import datetime
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
