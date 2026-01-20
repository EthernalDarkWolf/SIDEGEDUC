from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from database.models import Usuarios, Roles, StatusUser, db
from werkzeug.security import generate_password_hash, check_password_hash

login_bp = Blueprint('login', __name__)


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login/index.html')

    # POST
    usuario_nombre = request.form.get('usuario')
    clave = request.form.get('clave')

    if not usuario_nombre or not clave:
        # Mostrar mensaje sobrepuesto indicando credenciales faltantes/incorrectas
        mensaje = 'Acceso denegado usuario o clave incorrectos'
        return render_template('login/index.html', modal_show=True, modal_title='Acceso denegado', modal_message=mensaje)

    usuario = Usuarios.query.filter_by(nombre=usuario_nombre).first()

    if usuario:
        stored = usuario.contrasena
        if check_password_hash(stored, clave) or stored == clave:
           
            # Verificar estado del usuario aqui el status_user entra em juego si el usuario tiene un valor de inactivo/suspendido niega el acceso
            status = None
            try:
                status = StatusUser.query.filter_by(id_status_user=usuario.id_status_user).first()
            except Exception:
                status = None

            estado = (status.estado.lower() if status and status.estado else '')

            if 'suspend' in estado or 'suspendido' in estado:
                mensaje = 'No tienes permitido el acceso motivo: usuario suspendido'
                return render_template('login/index.html', modal_show=True, modal_title='Acceso denegado', modal_message=mensaje)

            if 'inactiv' in estado or 'inactivo' in estado:
                mensaje = 'No tienes permitido el acceso motivo: usuario Inactivo'
                return render_template('login/index.html', modal_show=True, modal_title='Acceso denegado', modal_message=mensaje)

            # Usuario activo: iniciar sesión
            session['user_id'] = usuario.id_user
            session['username'] = usuario.nombre
            return redirect(url_for('dashboard'))

    # Credenciales inválidas: mostrar mensaje sobrepuesto
    mensaje = 'Acceso denegado usuario o clave incorrectos'
    return render_template('login/index.html', modal_show=True, modal_title='Acceso denegado', modal_message=mensaje)


@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('login/register.html')

    nombre = request.form.get('usuario')
    clave = request.form.get('clave')

    if not nombre or not clave:
        # Mostrar mensaje indicando campos obligatorios en la página de login
        mensaje = 'Todos los campos son obligatorios'
        return render_template('login/index.html', modal_show=True, modal_title='Error', modal_message=mensaje)

    # Verificar si el usuario ya existe a la hora de registrar
    existing = Usuarios.query.filter_by(nombre=nombre).first()
    if existing:
        mensaje = 'El usuario ya existe'
        return render_template('login/index.html', modal_show=True, modal_title='Error', modal_message=mensaje)

    # Guardar usuario con role=1 y status_user=1 por defecto (esto cambiara)
    try:
        hashed = generate_password_hash(clave)
        nuevo = Usuarios(nombre=nombre, contrasena=hashed,
                         id_rol=1,
                         id_status_user=1)
        db.session.add(nuevo)
        db.session.commit()
        mensaje = f'Usuario {nombre} registrado exitosamente'
        return render_template('login/index.html', modal_show=True, modal_title='Registro exitoso', modal_message=mensaje)
    except Exception:
        db.session.rollback()
        mensaje = 'Error al crear usuario'
        return render_template('login/index.html', modal_show=True, modal_title='Error', modal_message=mensaje)

