from flask import Blueprint, request, jsonify, render_template, redirect, flash, session
from flask_login import login_user, logout_user
from config import settings
from datetime import datetime, timedelta

# Models
from src.models.usersModels import User

# Services
from src.services.AuthService import AuthService

main = Blueprint('auth_blueprint', __name__)



@main.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        try:
            username = request.form['username']
            password = request.form['password']
            _user = User(0, username, password, None)
            authenticated_user = AuthService.login_user(_user)
            if (authenticated_user != None):
                if authenticated_user.password == True: 
                    venc_token = datetime.now() + timedelta(hours=settings.VIDA_TOKEN)
                    login_user(authenticated_user, duration=venc_token)
                    session["_tipo_usuario"] = authenticated_user.tipo_usuario
                    if authenticated_user.tipo_usuario == 1 or authenticated_user.tipo_usuario == 2:
                        return redirect("/admin")
                    elif authenticated_user.tipo_usuario == 3:
                        return redirect("/stream")
                #return jsonify({'success': True, 'token': encoded_token})
            flash("Error, Usuario o contraseña incorrecta")
            return render_template('login.html')
        except Exception as ex:
            print(ex)
            return jsonify({'message': "ERROR", 'success': False})
        
@main.route('/logout')
def logout():
    logout_user()
    return redirect("/")