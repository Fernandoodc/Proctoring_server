import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout, Flatten
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import os


#Entrenamiento de un modelo de detección de aplicaciones usando MobileNetV2 sin ajuste fino

def train_module(category_name, data_path, epocas):
    # Configuración del dataset
    datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=0.3)
    train_gen = datagen.flow_from_directory(
        data_path,
        target_size=(400, 225),
        batch_size=16,
        class_mode='categorical',
        subset='training',
        color_mode='rgb'
    )
    val_gen = datagen.flow_from_directory(
        data_path,
        target_size=(400, 225),
        batch_size=16,
        class_mode='categorical',
        subset='validation',
        color_mode='rgb'
    )

    # Definición de la CNN
    base_model = MobileNetV2(input_shape=(400, 225, 3), include_top=False, weights="imagenet")
    base_model.trainable = False  # Congela las capas base

    # Construcción del modelo
    inputs = tf.keras.Input(shape=(400, 225, 3))
    x = base_model(inputs, training=False)
    #x = GlobalAveragePooling2D()(x)
    x = Flatten()(x)
    #x = Dropout(0.7)(x)
    outputs = Dense(2, activation="softmax")(x)

    model = Model(inputs, outputs)
    model.summary()

    # Compilación del modelo
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                  loss="categorical_crossentropy",
                  metrics=["accuracy"])

    history = model.fit(train_gen, validation_data=val_gen, epochs=epocas)

    # Guardar el modelo entrenado
    #model.save(f"{category_name}_model.h5")
    print(f"Modelo para {category_name} guardado.")

    # Graficar los resultados
    rango_epocas = range(epocas)
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.plot(rango_epocas, acc, label='Precisión Entrenamiento')
    plt.plot(rango_epocas, val_acc, label='Precisión Pruebas')
    plt.legend(loc='lower right')
    plt.title('Precisión del modelo')

    plt.subplot(1, 2, 2)
    plt.plot(rango_epocas, loss, label='Pérdida Entrenamiento')
    plt.plot(rango_epocas, val_loss, label='Pérdida Pruebas')
    plt.legend(loc='upper right')
    plt.title('Pérdida del modelo')

    plt.tight_layout()
    plt.show()


train_module('Nombre_modelo', 'dataset', 15)
