# Proctoring Server

Este proyecto es un **servidor de proctoring modular** basado en modelos de **redes neuronales convolucionales (CNN)**, diseñado para supervisar evaluaciones en computadoras y detectar en tiempo real el uso de programas o páginas web no autorizadas durante un examen. Su arquitectura modular permite agregar fácilmente nuevos modelos de detección sin modificar el sistema principal.

## ¿Qué hace este programa?

- Supervisa sesiones de examen en línea mediante la transmisión en directo de la pantalla del alumno al servidor.
- Detecta el uso de aplicaciones o sitios web no permitidos utilizando modelos de redes neuronales convolucionales (CNN) basados en MobileNetV2.
- Permite al docente seleccionar, al inicio de la evaluación, los modelos y programas permitidos (lista blanca).
- Genera alertas en tiempo real si se detecta el uso de software no autorizado.

## ¿Cómo funciona?

1. El docente define la lista blanca de programas y páginas web permitidas seleccionando los modelos correspondientes.
2. El alumno transmite su pantalla al servidor mediante una conexión WebSocket.
3. Cada fotograma recibido es analizado por los modelos CNN seleccionados, cada uno entrenado para reconocer un programa o página específica.
4. Si ningún modelo de la lista blanca reconoce el contenido del fotograma, se genera una alerta automática para el docente.
5. El sistema es modular, permitiendo agregar nuevos modelos fácilmente sin reentrenar el conjunto completo.

## Inicialización del programa

1. Clona el repositorio:
    ```bash
    git clone https://github.com/Fernandoodc/Proctoring_server.git
    cd Proctoring_server
    ```

2. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

3. Inicializa la base de datos ejecutando el siguiente comando:
    ```bash
    python inicializar.py
    ```
    Esto creará la base de datos y agregará un usuario administrador con usuario `admin` y contraseña `admin`.

4. Inicia el servidor:
    ```bash
    python main.py
    ```

5. Agrega usuarios, carga modelos y utiliza el programa según tus necesidades.

---

**Nota:** Asegúrate de tener Python instalado y configurado correctamente en tu sistema.
