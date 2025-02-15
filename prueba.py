from tensorflow.keras.models import load_model
import  os
dir_base="modelos"

print(os.listdir(dir_base))

# Ruta correcta al archivo del modelo
modelo_path = "modelos/facebookv2_400_mobilenet_fino_model.h5"

# Cargar el modelo
try:
    modelo = load_model(modelo_path)
    print("Modelo cargado correctamente.")
except OSError as e:
    print(f"Error al cargar el modelo: {e}")