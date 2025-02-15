from flask import Blueprint, request, jsonify, render_template, redirect, flash, session
from flask_login import login_required

main = Blueprint('alumno_blueprint', __name__)

@main.route('/', methods=['GET'])
@login_required
def stream():
    return render_template('stream.html')
