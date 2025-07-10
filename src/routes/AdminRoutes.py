from flask import Blueprint, request, render_template, redirect, flash, url_for
from flask_login import login_required
from src.models.modelosModels import Modelos
from src.decoradores import roles_required
from src.models.deteccionesModels import Detecciones
from src import MODELOS_SELECCIONADOS, socketio

main = Blueprint('admin_blueprint', __name__)

@main.route('/', methods=['GET'])
@login_required
def inicio():
    return render_template('inicio.html')

@main.route('/nuevo_examen', methods=['GET', 'POST'])
@login_required
@roles_required(2)
def nuevo_examen():
    if request.method == 'GET':
        modelos = Modelos.get_modelos()
        return render_template('nuevo_examen.html', modelos=modelos)
    elif request.method == 'POST':
        #nom_examen = request.form['nombre']
        modelosSelected = request.form.getlist('modelos')
        print(modelosSelected)
        global MODELOS_SELECCIONADOS
        for modelo in modelosSelected:
            if not int(modelo) in MODELOS_SELECCIONADOS:
                MODELOS_SELECCIONADOS.append(int(modelo))
        return redirect(url_for('admin_blueprint.stream'))

@main.route('/terminar_examen', methods=['GET'])
@login_required
@roles_required(2)
def terminar_examen():
    global MODELOS_SELECCIONADOS
    MODELOS_SELECCIONADOS = []
    mensaje = {
        'terminado': True
    }
    socketio.emit('terminar_examen', mensaje)
    return redirect(url_for('admin_blueprint.inicio'))

@main.route('/detecciones', methods=['GET'])
@login_required
@roles_required(2)
def stream():
    if MODELOS_SELECCIONADOS == []:
        return redirect(url_for('admin_blueprint.inicio'))
    return render_template('admin.html')

@main.route('/detecciones/imagen/<int:id>', methods=['GET'])
@login_required
def get_img(id):
    deteccion = Detecciones.get_img_deteccion(id)
    return render_template('imagen.html', deteccion=deteccion)

@main.route('modelos/', methods=['GET', 'POST'])
@login_required
@roles_required(1)
def modelos():
    if request.method == 'GET':
        modelos = Modelos.get_all_modelos()
        return render_template('modelos.html', modelos=modelos)
    else:
        nombre = request.form['nombre']
        file = request.files['modelo']
        salida = request.form['salida']
        if file.filename == '':
            flash("No se ha seleccionado un archivo", "error")
            return render_template('modelos.html')
        if not file.filename.endswith(".h5"):
            flash("El archivo seleccionado no es un modelo válido", "error")
            return render_template('modelos.html')  
        if nombre == "" or file == None or salida == "":
            flash("Faltan datos", "error")
            return render_template('modelos.html')
        Modelos.add_modelo(nombre, file, salida)
        modelos = Modelos.get_all_modelos()
        return render_template('modelos.html', modelos=modelos)

@main.route('modelos/desactivar_modelo/<int:id>', methods=['GET'])
@login_required
@roles_required(1)
def desactivar_modelo(id):
    Modelos.desactivar_modelo(id)
    return redirect(url_for('admin_blueprint.modelos'))

@main.route('modelos/activar_modelo/<int:id>', methods=['GET'])
@login_required
@roles_required(1)
def activar_modelo(id):
    Modelos.activar_modelo(id)
    return redirect(url_for('admin_blueprint.modelos'))