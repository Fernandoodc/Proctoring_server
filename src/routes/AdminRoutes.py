from flask import Blueprint, request, jsonify, render_template, redirect, flash, session, url_for
from flask_login import login_required
from src.models.modelosModels import Modelos
from src import MODELOS_SELECCIONADOS
from tensorflow.keras.models import load_model

main = Blueprint('admin_blueprint', __name__)

@main.route('/', methods=['GET'])
@login_required
def inicio():
    return render_template('inicio.html')

@main.route('/nuevo_examen', methods=['GET', 'POST'])
@login_required
def nuevo_examen():
    if request.method == 'GET':
        salidas = Modelos.get_all_salidas()
        return render_template('nuevo_examen.html', salidas=salidas)
    elif request.method == 'POST':
        nom_examen = request.form['nombre']
        salidas = request.form.getlist('salidas')
        print(salidas)
        global MODELOS_SELECCIONADOS
        for salida in salidas:
            modelo = Modelos.get_modelo_by_id_salida(int(salida))
            if not modelo in MODELOS_SELECCIONADOS:
                MODELOS_SELECCIONADOS.append(Modelos.get_modelo_by_id_salida(int(salida)).id_modelo)
        #loaded_models = {modelo.descripcion: load_model(modelo.path) for modelo in Modelos.get_modelos_by_ids(MODELOS_SELECCIONADOS)}
        return redirect(url_for('admin_blueprint.stream'))

@main.route('/terminar_examen', methods=['GET'])
@login_required
def terminar_examen():
    global MODELOS_SELECCIONADOS
    MODELOS_SELECCIONADOS = []
    return redirect(url_for('admin_blueprint.inicio'))

@main.route('/detecciones', methods=['GET'])
@login_required
def stream():
    return render_template('admin.html')

@main.route('modelos/', methods=['GET', 'POST'])
@login_required
def modelos():
    if request.method == 'GET':
        return render_template('modelos.html')
    else:
        nombre = request.form['nombre']
        file = request.files['modelo']
        salidas = request.form['salidas']
        if file.filename == '':
            flash("No se ha seleccionado un archivo", "error")
            return render_template('modelos.html')
        if not file.filename.endswith(".h5"):
            flash("El archivo seleccionado no es un modelo válido", "error")
            return render_template('modelos.html')  
        if nombre == "" or file == None or salidas == "":
            flash("Faltan datos", "error")
            return render_template('modelos.html')
        Modelos.add_modelo(nombre, file, salidas)
        return render_template('modelos.html')
