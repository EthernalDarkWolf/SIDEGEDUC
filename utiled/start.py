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
        return render_template('login/login_invalid.html')

    usuario = Usuarios.query.filter_by(nombre=usuario_nombre).first()

    if usuario:
        stored = usuario.contrasena
        if check_password_hash(stored, clave) or stored == clave:
            session['user_id'] = usuario.id_usuario
            session['username'] = usuario.nombre
            return redirect(url_for('dashboard'))

    return render_template('login/login_invalid.html')


@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('login/register.html')

    nombre = request.form.get('usuario')
    clave = request.form.get('clave')

    if not nombre or not clave:
        flash('Todos los campos son obligatorios')
        return redirect(url_for('login.register'))

    existing = Usuarios.query.filter_by(nombre=nombre).first()
    if existing:
        flash('El usuario ya existe')
        return redirect(url_for('login.register'))

    # asegurar role y status por defecto
    role = Roles.query.filter_by(nombre_rol='user').first()
    if not role:
        role = Roles(nombre_rol='user')
        try:
            db.session.add(role)
            db.session.commit()
        except Exception:
            db.session.rollback()

    status = StatusUser.query.filter_by(estado='active').first()
    if not status:
        try:
            status = StatusUser(estado='active')
            db.session.add(status)
            db.session.commit()
        except Exception:
            db.session.rollback()

    try:
        role = Roles.query.filter_by(nombre_rol='user').first()
        status = StatusUser.query.filter_by(estado='active').first()
        hashed = generate_password_hash(clave)
        nuevo = Usuarios(nombre=nombre, contrasena=hashed,
                         id_rol=role.id_rol if role else 1,
                         id_status_user=status.id_status_user if status else 1)
        db.session.add(nuevo)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash('Error al crear usuario')
        return redirect(url_for('login.register'))

    return render_template('login/register_success.html', usuario=nombre)

