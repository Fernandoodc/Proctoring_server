import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Flatten
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import os
import  numpy as np

#Entrenamiento de un modelo de detección de aplicaciones usando MobileNetV2 con ajuste fino


def train_module(category_name, data_path, epocas):
    # Configuración del dataset
    datagen = ImageDataGenerator(rescale=1.0/255,
                                width_shift_range = 0.10,
                                height_shift_range = 0.10,
                                rotation_range=30,
                                 zoom_range=0.2,
                                 horizontal_flip=True,
                                 brightness_range=[0.8, 1.2],
                                 shear_range=15,
                                 fill_mode='nearest',
                                validation_split=0.3)
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

    # Visualización de imágenes aumentadas
    def plot_augmented_images(generator, num_images=8):
        plt.figure(figsize=(15, 10))
        images, labels = next(generator)

        for i in range(num_images):
            plt.subplot(4, 4, i + 1)
            plt.imshow(images[i])
            plt.title(f'Class: {np.argmax(labels[i])}')
            plt.axis('off')
        plt.suptitle('Ejemplos de imágenes aumentadas', fontsize=16)
        plt.tight_layout()
        plt.show()

    # Mostrar imágenes aumentadas
    plot_augmented_images(train_gen)

    # Definición de la CNN
    # Carga del modelo base con MobileNetV2 y pesos preentrenados de ImageNet
    base_model = MobileNetV2(input_shape=(400,225, 3), include_top=False, weights="imagenet")
    base_model.trainable = False  # Congela las capas base

    # Construcción del modelo
    inputs = tf.keras.Input(shape=(400,225, 3))
    x = base_model(inputs, training=False)
    #x = GlobalAveragePooling2D()(x)
    x = Flatten()(x)
    x = Dropout(0.5)(x)
    outputs = Dense(2, activation="softmax")(x)

    model = Model(inputs, outputs)
    model.summary()

    # Compilación del modelo
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                loss="categorical_crossentropy",
                metrics=["accuracy"])
    

    history = model.fit(train_gen, validation_data=val_gen, epochs=epocas)

    # Descongela las capas base para ajuste fino (opcional)
    base_model.trainable = True
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.00001),
                loss="categorical_crossentropy",
                metrics=["accuracy"])
    history2 = model.fit(train_gen, validation_data=val_gen, epochs=10)
    
    # Guardar el modelo entrenado
    model.save(f"{category_name}_model.h5")
    print(f"Modelo para {category_name} guardado.")



    rango_epocas = range(epocas)

    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']

    loss = history.history['loss']
    val_loss = history.history['val_loss']

    # Graficar los resultados
    # Antes del ajuste fino
    rango_epocas = range(epocas)
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    plt.figure(figsize=(12, 6))
    plt.subplot(2, 2, 1)
    plt.plot(rango_epocas, acc, label='Precisión Entrenamiento')
    plt.plot(rango_epocas, val_acc, label='Precisión Pruebas')
    plt.legend(loc='lower right')
    plt.title('Precisión antes del ajuste fino')

    plt.subplot(2, 2, 2)
    plt.plot(rango_epocas, loss, label='Pérdida Entrenamiento')
    plt.plot(rango_epocas, val_loss, label='Pérdida Pruebas')
    plt.legend(loc='upper right')
    plt.title('Pérdida antes del ajuste fino')

    # Después del ajuste fino
    rango_epocas_fino = range(10)  # Ajuste fino tiene 5 épocas
    acc_fino = history2.history['accuracy']
    val_acc_fino = history2.history['val_accuracy']
    loss_fino = history2.history['loss']
    val_loss_fino = history2.history['val_loss']

    plt.subplot(2, 2, 3)
    plt.plot(rango_epocas_fino, acc_fino, label='Precisión Entrenamiento (ajuste fino)')
    plt.plot(rango_epocas_fino, val_acc_fino, label='Precisión Pruebas (ajuste fino)')
    plt.legend(loc='lower right')
    plt.title('Precisión después del ajuste fino')

    plt.subplot(2, 2, 4)
    plt.plot(rango_epocas_fino, loss_fino, label='Pérdida Entrenamiento (ajuste fino)')
    plt.plot(rango_epocas_fino, val_loss_fino, label='Pérdida Pruebas (ajuste fino)')
    plt.legend(loc='upper right')
    plt.title('Pérdida después del ajuste fino')

    plt.tight_layout()
    plt.show()



train_module('Nombre_modelo', 'dataset', 30)
