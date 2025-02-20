from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required
from src.decoradores import roles_required
from ..models.usersModels import User

main = Blueprint('usuarios_blueprint', __name__)

@main.route("/")
@login_required
@roles_required(1)
def viewUsuarios():
    usuarios = User.get_users()
    return render_template("usuarios/lista_usuarios.html", usuario = usuarios)

@main.route("agregar/", methods = ['GET', 'POST'])
@login_required
@roles_required(1)
def agregarUser():
    tipos_usuarios = User.get_tipos_usuarios()
    if request.method == 'GET':
        return render_template("usuarios/usuario.html", tipos_usuarios=tipos_usuarios)
    else:
        username = request.form['username']
        if User.get_by_username(username) != None:
            flash("El nombre de usuario ya se encuentra en uso.", "danger")
            return render_template("usuarios/usuario.html", tipos_usuarios=tipos_usuarios)
        password = request.form['password']
        nombre = request.form['nombre']
        documento = request.form['documento']
        tipo_user = request.form['tipo_usuario']
        userId = User.add_user(username, password, nombre, documento, tipo_user)
        flash("Usuario agregado correctamente", "success")
        return render_template("usuarios/usuario.html", tipos_usuarios=tipos_usuarios)


@main.route("<int:idUsuario>/editar", methods = ['GET', 'POST'])
@login_required
@roles_required(1)
def editarUsuario(idUsuario):
    usuario = User.get_full_by_id(idUsuario)
    tipos_usuarios = User.get_tipos_usuarios()
    if request.method == 'GET':
        tipo_user = User.get_tipo_by_id(idUsuario)
        return render_template("usuarios/editar_usuario.html", usuario = usuario, tipos_usuarios=tipos_usuarios, tipo_user = tipo_user)
    else:
        nombre = request.form['nombre']
        documento = request.form['documento']
        tipo_user = request.form['tipo_usuario']
        #newPermisos = request.form.getlist('permisos')
        User.update_user(idUsuario, nombre, documento, tipo_user)
        usuario = User.get_full_by_id(idUsuario)
        flash("Datos actualizados", "success")
        return render_template("usuarios/editar_usuario.html", usuario = usuario, tipos_usuarios=tipos_usuarios)
@main.route("<int:idUsuario>/password/reset", methods = ['GET', 'POST'])
@login_required
@roles_required(1)
def resetPassword(idUsuario):
    usuario = User.get_by_id(idUsuario)
    if request.method == 'GET':
        return render_template("usuarios/reset_password.html", usuario = usuario)
    else:
        password = request.form['password']
        User.set_new_password_by_id(idUsuario, password)
        flash('Contraseña actualizada correctamente', 'success')
        return render_template("usuarios/reset_password.html", usuario = usuario)

@main.route("<int:idUsuario>/password/", methods = ['GET', 'POST'])
@login_required
def updatePassword(idUsuario):
    current_user = User.current_user_id()
    if int(current_user) != int(idUsuario):
        return {
            "msg": "Error, no tiene permisos para realizar esta acción"
        }
    if request.method == 'GET':
        return render_template("usuarios/update_password.html")
    else:
        usuario = User.get_by_id(idUsuario)
        password = request.form['password']
        newPassword = request.form['newPassword']
        if User.check_password(usuario.password, password):
            User.set_new_password_by_id(idUsuario, newPassword)
            flash('Contraseña actualizada correctamente', 'success')
        else:
            flash('Contraseña incorrecta, intente de nuevo', 'danger')
        return render_template("usuarios/update_password.html")

@main.route("<int:idUsuario>/desactivar", methods = ['GET'])
@login_required
@roles_required(1)
def desactivarUsuario(idUsuario):
    User.set_inactivo_by_id(idUsuario)
    return redirect(url_for("usuarios_blueprint.viewUsuarios"))

@main.route("<int:idUsuario>/activar", methods = ['GET'])
@login_required
@roles_required(1)
def activarUsuario(idUsuario):
    User.set_activo_by_id(idUsuario)
    return redirect(url_for("usuarios_blueprint.viewUsuarios"))

@main.route("verif_username/", methods = ['GET'])
@login_required
@roles_required(1)
def verifUsername():
    username = request.args['username']
    user = User.get_by_username(username)
    if user == None:
        return {
            'msg': 'Usuario disponible'
        }
    else:
        return {
            'msg': 'Usuario no disponible'
        }, 409