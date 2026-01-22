#el  codigo de este script es para el manejo de la bd y funciones del sistema junto con ella

from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from database.models import Usuarios, Roles, StatusUser, db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import OperationalError

login_bp = Blueprint('login', __name__)


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login/index.html', active='login')

    # obtener datos  de la bd para verificar credenciales
    usuario_nombre = request.form.get('usuario')
    clave = request.form.get('clave')

    if not usuario_nombre or not clave:
        # Mostrar mensaje sobrepuesto indicando credenciales faltantes/incorrectas
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
           
            # Verificar estado del usuario aqui el status_user entra em juego si el usuario tiene un valor de inactivo/suspendido niega el acceso
            status = None
            try:
                status = StatusUser.query.filter_by(id_status_user=usuario.id_status_user).first()
            except Exception:
                status = None

            estado = (status.estado.lower() if status and status.estado else '')

            #condiciones para estados de usuario (para  que sea mejor el mensaje de error, y se especifico segun el caso)
            if 'suspend' in estado or 'suspendido' in estado:
                mensaje = 'No tienes permitido el acceso motivo: usuario suspendido'
                return render_template('login/index.html', modal_show=True, modal_title='Acceso denegado', modal_message=mensaje, active='login')

            if 'inactiv' in estado or 'inactivo' in estado:
                mensaje = 'No tienes permitido el acceso motivo: usuario Inactivo'
                return render_template('login/index.html', modal_show=True, modal_title='Acceso denegado', modal_message=mensaje, active='login')

            # Usuario activo: iniciar sesión (si el usuario esta inactivo o suspendido no le permite el acceso)
            session['user_id'] = usuario.id_user
            session['username'] = usuario.nombre
            return redirect(url_for('dashboard'))

    # Credenciales inválidas: mostrar mensaje sobrepuesto
    mensaje = 'Acceso denegado usuario o clave incorrectos'
    return render_template('login/index.html', modal_show=True, modal_title='Acceso denegado', modal_message=mensaje, active='login')


@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # Renderizar la plantilla combinada y seleccionar la pestaña de registro
        return render_template('login/index.html', active='register')

    nombre = request.form.get('usuario')
    clave = request.form.get('clave')

    # Validación server-side: el usuario debe aceptar los términos para poder registrarse
    terms = request.form.get('terms')
    if not terms:
        mensaje = 'Debes aceptar los términos de servicio para crear la cuenta.'
        return render_template('login/index.html', modal_show=True, modal_title='Error', modal_message=mensaje, active='register')

    if not nombre or not clave:
        # Mostrar mensaje indicando campos obligatorios en la página de login (por si alguien se le ocurre no ingesar algo en el login)
        mensaje = 'Todos los campos son obligatorios'
        return render_template('login/index.html', modal_show=True, modal_title='Error', modal_message=mensaje, active='register')

    # Verificar si el usuario ya existe a la hora de registrar si ay otro username igual pues.. mostrar error 
    try:
        existing = Usuarios.query.filter_by(nombre=nombre).first()
    except OperationalError:
        mensaje = 'Error: no se puede conectar a la base de datos. Contacte a los Desarrolladores.'
        return render_template('login/index.html', modal_show=True, modal_title='Error BD', modal_message=mensaje, active='register')
    if existing:
        mensaje = 'El usuario ya existe'
        return render_template('login/index.html', modal_show=True, modal_title='Error', modal_message=mensaje, active='register')

    # Guardar usuario con rol=1 y status_user=1 por defecto (esto cambiara proxiamente)
    try: #  intentar crear el usuario y incriptar la clave en bd uwu
        hashed = generate_password_hash(clave)
        nuevo = Usuarios(nombre=nombre, contrasena=hashed, id_rol=1, id_status_user=1)
        db.session.add(nuevo)
        db.session.commit()
        mensaje = f'Usuario {nombre} registrado exitosamente'
        return render_template('login/index.html', modal_show=True, modal_title='Registro exitoso', modal_message=mensaje, active='login')
    except Exception: #manejo si ubo algun error al crear usuario
        db.session.rollback()
        mensaje = 'Error al crear usuario'
        return render_template('login/index.html', modal_show=True, modal_title='Error', modal_message=mensaje, active='register')

