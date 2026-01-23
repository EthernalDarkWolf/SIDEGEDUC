""" este script se encarga para las vistas del sistema
 es decir el encargado de renderizar las vistas.
dependiendo de los permisos que tenga el usuario y por su puesto
su estado de actividad, tambien se encarga de hacer algunos de los registros aunque
esto ultimo mas adelante ya no estara en este archivo..."""

from flask import render_template, redirect, url_for, request, session
from database.models import Usuarios, Roles, StatusUser, db
from .permissions import get_user_context, user_has_admin_privileges


def dashboard_view():
    #Muestra la página principal del dashboard 
    ctx = get_user_context(session)
    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'])


def index_view():
    #Ruta raíz; redirige al dashboard si hay sesión activa, al login si no
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login.login_handler'))


def boleta_view():
    return 'Boleta - en desarrollo'


def constancia_view():
    return 'Constancia - en desarrollo'


def admin_alumnos_view():
    return 'Administración de alumnos - en desarrollo'


def registros_index_view():
    #Lista de registros — reutiliza el contexto de usuario para permisos
    ctx = get_user_context(session)
    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], content_template='home_panel/registros.html')


def registros_tipo_view(tipo):
    allowed = ['plantel', 'estudiantes', 'profesores', 'personal_admin', 'personal_obrero']
    if tipo not in allowed: #quiere decir que no es un tipo valido
        return 'Tipo de registro no válido', 404
    title_map = {
        'plantel': 'Registro de Plantel',
        'estudiantes': 'Registro de Estudiantes',
        'profesores': 'Registro de Profesores',
        'personal_admin': 'Registro Personal Administrativo',
        'personal_obrero': 'Registro Personal Obrero'
    }
    ctx = get_user_context(session)
    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], content_template='home_panel/registro_tipo.html', tipo=tipo, title=title_map.get(tipo, 'Registro'))


def developer_manage_user_view():
    """Vista para que desarrolladores/administradores gestionen usuarios.

    - Si no hay sesión activa, redirige al login
    - Comprueba permisos usando `user_has_admin_privileges`
    - Maneja GET y POST para actualizar rol/estado
    """
    if 'user_id' not in session:
        return redirect(url_for('login.login_handler'))

    cur = Usuarios.query.filter_by(id_user=session.get('user_id')).first()
    if not cur:
        return redirect(url_for('login.login_handler'))

    if not user_has_admin_privileges(session):
        return 'Acceso denegado: privilegios insuficientes', 403

    # Preparar datos para el formulario
    users = Usuarios.query.filter(Usuarios.id_user != cur.id_user).order_by(Usuarios.nombre).all()
    roles = Roles.query.order_by(Roles.nombre_rol).all()
    statuses = StatusUser.query.order_by(StatusUser.estado).all()

    ctx = get_user_context(session)
    user = ctx['user']
    developer_priv = True
    current_user_id = ctx['current_user_id']

    if request.method == 'POST':
        form = request.form
        target = form.get('user_id')
        new_role = form.get('role_id')
        new_status = form.get('status_id')
        if target:
            target_user = Usuarios.query.filter_by(id_user=int(target)).first()
            if target_user:
                try:
                    if new_role:
                        target_user.id_rol = int(new_role)
                    if new_status:
                        target_user.id_status_user = int(new_status)
                    db.session.commit()
                    return render_template('home_panel/struct.html', usuario=user, developer_priv=developer_priv, content_template='home_panel/manage_user.html', users=users, roles=roles, statuses=statuses, message='Usuario actualizado correctamente', current_user_id=current_user_id)
                except Exception:
                    db.session.rollback()
                    return render_template('home_panel/struct.html', usuario=user, developer_priv=developer_priv, content_template='home_panel/manage_user.html', users=users, roles=roles, statuses=statuses, message='Error al actualizar el usuario', current_user_id=current_user_id)

    return render_template('home_panel/struct.html', usuario=user, developer_priv=developer_priv, content_template='home_panel/manage_user.html', users=users, roles=roles, statuses=statuses, current_user_id=current_user_id)
