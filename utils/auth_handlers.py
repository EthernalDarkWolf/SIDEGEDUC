#este archivo contiene la logica de las rutas de autenticacion como login y registro 

from flask import render_template, request, redirect, url_for, session
from database.models import Usuarios, Roles, StatusUser, db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import OperationalError


def login_handler():
    if request.method == 'GET':
        return render_template('login/index.html', active='login')

    usuario_nombre = request.form.get('usuario')
    clave = request.form.get('clave')

    if not usuario_nombre or not clave:
        mensaje = 'Acceso denegado usuario o clave incorrectos'
        return render_template('login/index.html', modal_show=True, modal_title='Acceso denegado', modal_message=mensaje, active='login')

    try:
        usuario = Usuarios.query.filter_by(nombre=usuario_nombre).first()
    except OperationalError:
        mensaje = 'Error: no se puede conectar a la base de datos. Contacte a los Desarrolladores.'
        return render_template('login/index.html', modal_show=True, modal_title='Error BD', modal_message=mensaje, active='login')

    if usuario:
        stored = usuario.contrasena
        if check_password_hash(stored, clave) or stored == clave:
            status = None
            try:
                status = StatusUser.query.filter_by(id_status_user=usuario.id_status_user).first()
            except Exception:
                status = None

            estado = (status.estado.lower() if status and status.estado else '')

            if 'suspend' in estado or 'suspendido' in estado:
                mensaje = 'No tienes permitido el acceso motivo: usuario suspendido'
                return render_template('login/index.html', modal_show=True, modal_title='Acceso denegado', modal_message=mensaje, active='login')

            if 'inactiv' in estado or 'inactivo' in estado:
                mensaje = 'No tienes permitido el acceso motivo: usuario Inactivo'
                return render_template('login/index.html', modal_show=True, modal_title='Acceso denegado', modal_message=mensaje, active='login')

            session['user_id'] = usuario.id_user
            session['username'] = usuario.nombre
            return redirect(url_for('dashboard'))

    mensaje = 'Acceso denegado usuario o clave incorrectos'
    return render_template('login/index.html', modal_show=True, modal_title='Acceso denegado', modal_message=mensaje, active='login')


def register_handler():
    if request.method == 'GET':
        return render_template('login/index.html', active='register')

    nombre = request.form.get('usuario')
    clave = request.form.get('clave')

    terms = request.form.get('terms')
    if not terms:
        mensaje = 'Debes aceptar los términos de servicio para crear la cuenta.'
        return render_template('login/index.html', modal_show=True, modal_title='Error', modal_message=mensaje, active='register')

    if not nombre or not clave:
        mensaje = 'Todos los campos son obligatorios'
        return render_template('login/index.html', modal_show=True, modal_title='Error', modal_message=mensaje, active='register')

    try:
        existing = Usuarios.query.filter_by(nombre=nombre).first()
    except OperationalError:
        mensaje = 'Error: no se puede conectar a la base de datos. Contacte a los Desarrolladores.'
        return render_template('login/index.html', modal_show=True, modal_title='Error BD', modal_message=mensaje, active='register')
    if existing:
        mensaje = 'El usuario ya existe'
        return render_template('login/index.html', modal_show=True, modal_title='Error', modal_message=mensaje, active='register')

    try:
        hashed = generate_password_hash(clave)
        nuevo = Usuarios(nombre=nombre, contrasena=hashed, id_rol=1, id_status_user=1)
        db.session.add(nuevo)
        db.session.commit()
        mensaje = f'Usuario {nombre} registrado exitosamente'
        return render_template('login/index.html', modal_show=True, modal_title='Registro exitoso', modal_message=mensaje, active='login')
    except Exception:
        db.session.rollback()
        mensaje = 'Error al crear usuario'
        return render_template('login/index.html', modal_show=True, modal_title='Error', modal_message=mensaje, active='register')
