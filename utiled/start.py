from flask import Blueprint, request, redirect, url_for, render_template, session
from database.models import Usuarios

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        contrasena = request.form['contrasena']

        usuario = Usuarios.query.filter_by(nombre=nombre, contrasena=contrasena).first()

        if usuario:
            session['user_id'] = usuario.id_usuario
            return redirect(url_for('dashboard')) 
        else:
            return 'Credenciales incorrectas'

    