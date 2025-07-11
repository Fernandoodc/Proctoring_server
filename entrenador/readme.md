# 📦 Carpeta `entrenador/`

Esta carpeta contiene **scripts de ejemplo y recursos** para entrenar modelos de redes neuronales convolucionales (CNN) que puedan integrarse de forma modular al servidor de proctoring.

El objetivo es facilitar la creación de nuevos modelos, cada uno especializado en reconocer un único programa o página web específica.

---

## 🧠 ¿Qué hacen estos scripts?

- Permiten entrenar modelos que identifiquen exclusivamente un programa o aplicación concreta.
- Generan archivos `.h5` compatibles con el servidor principal, listos para ser registrados en la base de datos y utilizados durante la supervisión en tiempo real.

---

## 📂 Estructura del dataset

Dentro de la carpeta `dataset/` encontrarás un ejemplo de organización del conjunto de datos usado para el entrenamiento:

- `dataset/1_programa_objetivo/`  
  Contiene capturas correspondientes **al programa específico que el modelo debe reconocer**.  
  Estas imágenes actúan como ejemplos positivos y permiten que la red neuronal aprenda a identificar correctamente la aplicación de interés.

- `dataset/2_otros_programas/`  
  Incluye capturas de pantalla de **aplicaciones distintas al programa objetivo**.  
  Su propósito es proporcionar ejemplos negativos para que el modelo aprenda a diferenciar entre lo que debe reconocer y todo lo demás.

---

## ✅ Recomendaciones para entrenar modelos compatibles

- Usa arquitecturas ligeras (como MobileNetV2) para permitir predicciones rápidas y consumo moderado de recursos.
- Ajusta las imágenes de entrada al tamaño esperado por el servidor (por ejemplo, `224x224` píxeles en RGB).
- Guarda los modelos exportados en formato `.h5` compatible con `keras.models.load_model()`.
- Asigna nombres descriptivos a los modelos (`word_model.h5`, `chrome_model.h5`), facilitando su identificación y mantenimiento.
- Cada modelo debe estar entrenado para reconocer **únicamente un programa o página web**.

---

## 🚀 ¿Cómo usar los scripts?

1. Prepara las capturas de pantalla necesarias y colócalas en las carpetas `dataset/1_programa_objetivo` y `dataset/2_otros_programas`.
2. Modifica el script de entrenamiento para ajustar rutas, hiperparámetros y clases según el caso.
3. Ejecuta el script para entrenar el modelo.
4. Agrega el modelo entrenado al sistema y reinicia el servidor para que pueda ser usado durante las evaluaciones.
