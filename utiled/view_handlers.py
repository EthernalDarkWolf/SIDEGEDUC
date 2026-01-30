""" este script se encarga para las vistas del sistema
 es decir el encargado de renderizar las vistas.
dependiendo de los permisos que tenga el usuario y por su puesto
su estado de actividad, tambien se encarga de hacer algunos de los registros aunque
esto ultimo mas adelante ya no estara en este archivo..."""

from flask import render_template, redirect, url_for, request, session
from database.models import Usuarios, Roles, StatusUser, db
from sqlalchemy import func, text
from .permissions import get_user_context, user_has_admin_privileges
from flask import abort
import os


def dashboard_view():
    #Muestra la página principal del dashboard 
    ctx = get_user_context(session)
    # Conteos: total de roles y usuarios por rol
    try:
        roles_count = Roles.query.count()
        users_q = db.session.query(Roles.nombre_rol, func.count(Usuarios.id_user)).join(Usuarios, Usuarios.id_rol == Roles.id_rol).group_by(Roles.id_rol).all()
        users_by_role = [{'role': r or 'Sin nombre', 'count': int(c)} for r, c in users_q]
    except Exception:
        roles_count = 0
        users_by_role = []

    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role)


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
    # provide counts in case template wants them
    try:
        roles_count = Roles.query.count()
        users_q = db.session.query(Roles.nombre_rol, func.count(Usuarios.id_user)).join(Usuarios, Usuarios.id_rol == Roles.id_rol).group_by(Roles.id_rol).all()
        users_by_role = [{'role': r or 'Sin nombre', 'count': int(c)} for r, c in users_q]
    except Exception:
        roles_count = 0
        users_by_role = []

    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registros.html')


def registros_tipo_view(tipo):
    # Solo permitir tipos manejables directamente desde este endpoint.
    # Los tipos específicos de persona (estudiante/profesor/empleado) se manejan
    # a través del flujo "personas" -> extensión (registro_persona_ext).
    allowed = ['plantel', 'personas', 'materias', 'secciones', 'letra_seccion', 'grados', 'niveles']
    # Inicializar variables para evitar errores de variable local no asociada
    roles_count = 0
    users_by_role = []
    message = None
    ctx = get_user_context(session)
    title_map = {
        'plantel': 'Registro de Plantel',
        'materias': 'Registro de Materias',
        'secciones': 'Registro de Secciones',
        'letra_seccion': 'Registro de Letra de Sección',
        'grados': 'Registro de Grados',
        'niveles': 'Registro de Niveles'
    }
    if tipo not in allowed: #quiere decir que no es un tipo valido
        abort(404, 'Tipo de registro no válido')

    # Si estamos registrando personas, manejar GET/POST para crear persona + tipo específico
    if tipo == 'personas':
        if request.method == 'POST':
            form = request.form
            primer = form.get('primer_nombre')
            segundo = form.get('segundo_nombre')
            papellido = form.get('primer_apellido')
            sapellido = form.get('segundo_apellido')
            fecha_nac = form.get('fecha_nacimiento')
            tipo_persona = form.get('tipo_persona')  # estudiante | representante | profesor | empleado
            id_sexo = form.get('id_sexo') or None
            id_tipo_documento = form.get('id_tipo_documento') or None
            numero_cedula = form.get('numero_cedula') or None
            # Validar campos requeridos
            if not primer or not papellido or not fecha_nac or not tipo_persona:
                message = 'Campos requeridos faltantes.'
            try:
                # insertar persona
                insert_person = text("INSERT INTO personas (primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, fecha_nacimiento, id_sexo, tipo_persona) VALUES (:primer, :segundo, :papellido, :sapellido, :fecha_nac, :id_sexo, :tipo_persona)")
                db.session.execute(insert_person, {'primer': primer, 'segundo': segundo or None, 'papellido': papellido, 'sapellido': sapellido or None, 'fecha_nac': fecha_nac or None, 'id_sexo': id_sexo, 'tipo_persona': tipo_persona})
                db.session.commit()
                # obtener id_persona recién insertada
                result = db.session.execute(text('SELECT LAST_INSERT_ID() as id'))
                new_id = int(result.fetchone()[0])

                # En vez de insertar la extensión aquí, redirigimos al formulario de extensión
                message = 'Persona creada. Por favor completa los datos adicionales.'
                return redirect(url_for('registro_persona_ext', pid=new_id, tipo=tipo_persona))
            except Exception as e:
                db.session.rollback()
                message = f'Error al registrar persona: {str(e)}'

            # pasar conteos y mostrar mensaje
            try:
                roles_count = Roles.query.count()
                users_q = db.session.query(Roles.nombre_rol, func.count(Usuarios.id_user)).join(Usuarios, Usuarios.id_rol == Roles.id_rol).group_by(Roles.id_rol).all()
                users_by_role = [{'role': r or 'Sin nombre', 'count': int(c)} for r, c in users_q]
            except Exception:
                roles_count = 0
                users_by_role = []
            return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_persona_v2.html', message=message)

        # GET: mostrar formulario
        try:
            roles_count = Roles.query.count()
            users_q = db.session.query(Roles.nombre_rol, func.count(Usuarios.id_user)).join(Usuarios, Usuarios.id_rol == Roles.id_rol).group_by(Roles.id_rol).all()
            users_by_role = [{'role': r or 'Sin nombre', 'count': int(c)} for r, c in users_q]
        except Exception:
            roles_count = 0
            users_by_role = []

        # cargar opciones necesarias: sexos y tipos de documento
        try:
            sexos = db.session.execute(text('SELECT id_sexo, letra_sexo FROM sexo')).fetchall()
        except Exception:
            sexos = []
        try:
            tipo_documentos = db.session.execute(text('SELECT id_tipo_documento, nombre_tipo_documento FROM tipo_documento')).fetchall()
        except Exception:
            tipo_documentos = []
        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_persona_v2.html', sexos=sexos, tipo_documentos=tipo_documentos)
    # Registrar plantel
    if tipo == 'plantel':
        if request.method == 'POST':
            form = request.form
            nombre = form.get('nombre_plantel_nomina')
            codigo_pa = form.get('codigo_pa')
            id_nivel = form.get('id_nivel') or None
            id_cargo = form.get('id_cargo') or None
            try:
                insert_sql = text("INSERT INTO planteles (codigo_pa, nombre_plantel_nomina, id_nivel, id_cargo) VALUES (:codigo_pa, :nombre, :id_nivel, :id_cargo)")
                db.session.execute(insert_sql, {'codigo_pa': codigo_pa, 'nombre': nombre, 'id_nivel': id_nivel, 'id_cargo': id_cargo})
                db.session.commit()
                message = 'Plantel registrado correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error al registrar plantel: {str(e)}'

            # cargar selects necesarios
            niveles = db.session.execute(text('SELECT id_nivel, nombre_nivel FROM niveles')).fetchall()
            cargos = db.session.execute(text('SELECT id_cargo, nombre_cargo FROM cargos')).fetchall()
            return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_plantel.html', niveles=niveles, cargos=cargos, message=message)

        # GET: mostrar formulario con selects
        niveles = db.session.execute(text('SELECT id_nivel, nombre_nivel FROM niveles')).fetchall()
        cargos = db.session.execute(text('SELECT id_cargo, nombre_cargo FROM cargos')).fetchall()
        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_plantel.html', niveles=niveles, cargos=cargos)

    # Gestion de materias
    if tipo == 'materias':
        if request.method == 'POST':
            form = request.form
            nombre_materia = form.get('nombre_materia')
            try:
                db.session.execute(text('INSERT INTO materias (nombre_materia) VALUES (:name)'), {'name': nombre_materia})
                db.session.commit()
                message = 'Materia creada correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error al crear materia: {str(e)}'

            return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_materias.html', message=message)

        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_materias.html')

    # Gestion de secciones (crear sección simple)
    if tipo == 'secciones':
        if request.method == 'POST':
            form = request.form
            id_letra = form.get('id_letra_seccion') or None
            id_grado = form.get('id_grado') or None
            id_nivel = form.get('id_nivel') or None
            try:
                db.session.execute(text('INSERT INTO secciones (id_letra_seccion, id_grado, id_nivel) VALUES (:id_letra, :id_grado, :id_nivel)'), {'id_letra': id_letra, 'id_grado': id_grado, 'id_nivel': id_nivel})
                db.session.commit()
                message = 'Sección creada correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error al crear sección: {str(e)}'

            # recargar selects
            try:
                letras = db.session.execute(text('SELECT id_letra_seccion, letra FROM letra_seccion')).fetchall()
            except Exception:
                letras = []
            try:
                grados = db.session.execute(text('SELECT id_grado, numero_grado FROM grados')).fetchall()
            except Exception:
                grados = []
            try:
                niveles = db.session.execute(text('SELECT id_nivel, nombre_nivel FROM niveles')).fetchall()
            except Exception:
                niveles = []

            return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_secciones.html', letras=letras, grados=grados, niveles=niveles, message=message)

        # GET: mostrar formulario con selects
        try:
            letras = db.session.execute(text('SELECT id_letra_seccion, letra FROM letra_seccion')).fetchall()
        except Exception:
            letras = []
        try:
            grados = db.session.execute(text('SELECT id_grado, numero_grado FROM grados')).fetchall()
        except Exception:
            grados = []
        try:
            niveles = db.session.execute(text('SELECT id_nivel, nombre_nivel FROM niveles')).fetchall()
        except Exception:
            niveles = []

        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_secciones.html', letras=letras, grados=grados, niveles=niveles)

    action = request.args.get('action')
    if action == 'add_student':
        if request.method == 'POST':
            form = request.form
            id_estudiante = form.get('id_estudiante')
            id_seccion = form.get('id_seccion')
            try:
                db.session.execute(text('INSERT INTO estudiante_seccion (id_estudiante, id_seccion) VALUES (:est, :sec)'), {'est': id_estudiante, 'sec': id_seccion})
                db.session.commit()
                message = 'Estudiante asignado a sección correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error: {str(e)}'
            estudiantes = db.session.execute(text('SELECT e.id_estudiante, p.primer_nombre, p.primer_apellido FROM estudiantes e JOIN personas p ON e.id_persona = p.id_persona')).fetchall()
            secciones = db.session.execute(text('SELECT id_seccion, id_grado, id_letra_seccion FROM secciones')).fetchall()
            return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_secciones.html', estudiantes=estudiantes, secciones=secciones, message=message, action=action)
        estudiantes = db.session.execute(text('SELECT e.id_estudiante, p.primer_nombre, p.primer_apellido FROM estudiantes e JOIN personas p ON e.id_persona = p.id_persona')).fetchall()
        secciones = db.session.execute(text('SELECT id_seccion, id_grado, id_letra_seccion FROM secciones')).fetchall()
        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_secciones.html', estudiantes=estudiantes, secciones=secciones, action=action)

    if action == 'assign_professor':
        if request.method == 'POST':
            form = request.form
            id_profesor = form.get('id_profesor')
            id_seccion = form.get('id_seccion')
            try:
                db.session.execute(text('INSERT INTO profesor_seccion (id_profesor, id_seccion) VALUES (:prof, :sec)'), {'prof': id_profesor, 'sec': id_seccion})
                db.session.commit()
                message = 'Profesor asignado a sección correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error: {str(e)}'
            profesores = db.session.execute(text('SELECT pr.id_profesor, p.primer_nombre, p.primer_apellido FROM profesores pr JOIN personas p ON pr.id_persona = p.id_persona')).fetchall()
            secciones = db.session.execute(text('SELECT id_seccion, id_grado, id_letra_seccion FROM secciones')).fetchall()
            return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_secciones.html', profesores=profesores, secciones=secciones, message=message, action=action)
        profesores = db.session.execute(text('SELECT pr.id_profesor, p.primer_nombre, p.primer_apellido FROM profesores pr JOIN personas p ON pr.id_persona = p.id_persona')).fetchall()
        secciones = db.session.execute(text('SELECT id_seccion, id_grado, id_letra_seccion FROM secciones')).fetchall()
        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_secciones.html', profesores=profesores, secciones=secciones, action=action)

    if action == 'assign_materia':
        selected_seccion = request.args.get('seccion_id')
        if request.method == 'POST':
            form = request.form
            id_materia = form.get('id_materia')
            id_seccion = form.get('id_seccion')
            try:
                db.session.execute(text('INSERT INTO materias_seccion (id_materia, id_seccion) VALUES (:mid, :sid)'), {'mid': id_materia, 'sid': id_seccion})
                db.session.commit()
                message = 'Materia asignada a sección correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error: {str(e)}'
            # recargar
            try:
                secciones = db.session.execute(text('SELECT id_seccion, id_grado, id_letra_seccion FROM secciones')).fetchall()
            except Exception:
                secciones = []
            try:
                materias = db.session.execute(text('SELECT id_materia, nombre_materia FROM materias')).fetchall()
            except Exception:
                materias = []
            materias_asignadas = []
            if id_seccion:
                try:
                    materias_asignadas = db.session.execute(text('SELECT m.id_materia, m.nombre_materia FROM materias m JOIN materias_seccion ms ON ms.id_materia = m.id_materia WHERE ms.id_seccion = :sid'), {'sid': id_seccion}).fetchall()
                except Exception:
                    materias_asignadas = []
            return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_secciones.html', secciones=secciones, materias=materias, materias_asignadas=materias_asignadas, selected_seccion=int(id_seccion) if id_seccion else None, message=message, action=action)
        # GET
        try:
            secciones = db.session.execute(text('SELECT id_seccion, id_grado, id_letra_seccion FROM secciones')).fetchall()
        except Exception:
            secciones = []
        try:
            materias = db.session.execute(text('SELECT id_materia, nombre_materia FROM materias')).fetchall()
        except Exception:
            materias = []
        materias_asignadas = []
        if selected_seccion:
            try:
                materias_asignadas = db.session.execute(text('SELECT m.id_materia, m.nombre_materia FROM materias m JOIN materias_seccion ms ON ms.id_materia = m.id_materia WHERE ms.id_seccion = :sid'), {'sid': selected_seccion}).fetchall()
            except Exception:
                materias_asignadas = []
        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_secciones.html', secciones=secciones, materias=materias, materias_asignadas=materias_asignadas, selected_seccion=int(selected_seccion) if selected_seccion else None, action=action)

    if tipo == 'letra_seccion':
        if request.method == 'POST':
            form = request.form
            letra = form.get('letra')
            try:
                db.session.execute(text('INSERT INTO letra_seccion (letra) VALUES (:letra)'), {'letra': letra})
                db.session.commit()
                message = 'Letra de sección creada correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error: {str(e)}'
            return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_tipo.html', tipo=tipo, title=title_map.get(tipo, 'Registro'), message=message)
        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_tipo.html', tipo=tipo, title=title_map.get(tipo, 'Registro'))

    if tipo == 'grados':
        if request.method == 'POST':
            form = request.form
            numero_grado = form.get('numero_grado')
            try:
                db.session.execute(text('INSERT INTO grados (numero_grado) VALUES (:numero)'), {'numero': numero_grado})
                db.session.commit()
                message = 'Grado creado correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error: {str(e)}'
            return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_tipo.html', tipo=tipo, title=title_map.get(tipo, 'Registro'), message=message)
        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_tipo.html', tipo=tipo, title=title_map.get(tipo, 'Registro'))

    if tipo == 'niveles':
        if request.method == 'POST':
            form = request.form
            nombre_nivel = form.get('nombre_nivel')
            try:
                db.session.execute(text('INSERT INTO niveles (nombre_nivel) VALUES (:nombre)'), {'nombre': nombre_nivel})
                db.session.commit()
                message = 'Nivel creado correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error: {str(e)}'
            return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_tipo.html', tipo=tipo, title=title_map.get(tipo, 'Registro'), message=message)
        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_tipo.html', tipo=tipo, title=title_map.get(tipo, 'Registro'))

    # Default behavior for other tipos
    try:
        roles_count = Roles.query.count()
        users_q = db.session.query(Roles.nombre_rol, func.count(Usuarios.id_user)).join(Usuarios, Usuarios.id_rol == Roles.id_rol).group_by(Roles.id_rol).all()
        users_by_role = [{'role': r or 'Sin nombre', 'count': int(c)} for r, c in users_q]
    except Exception:
        roles_count = 0
        users_by_role = []

    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_tipo.html', tipo=tipo, title=title_map.get(tipo, 'Registro'))


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
                    try:
                        roles_count = Roles.query.count()
                        users_q = db.session.query(Roles.nombre_rol, func.count(Usuarios.id_user)).join(Usuarios, Usuarios.id_rol == Roles.id_rol).group_by(Roles.id_rol).all()
                        users_by_role = [{'role': r or 'Sin nombre', 'count': int(c)} for r, c in users_q]
                    except Exception:
                        roles_count = 0
                        users_by_role = []
                    return render_template('home_panel/struct.html', usuario=user, developer_priv=developer_priv, role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/manage_user.html', users=users, roles=roles, statuses=statuses, message='Usuario actualizado correctamente', current_user_id=current_user_id)
                except Exception:
                    db.session.rollback()
                    try:
                        roles_count = Roles.query.count()
                        users_q = db.session.query(Roles.nombre_rol, func.count(Usuarios.id_user)).join(Usuarios, Usuarios.id_rol == Roles.id_rol).group_by(Roles.id_rol).all()
                        users_by_role = [{'role': r or 'Sin nombre', 'count': int(c)} for r, c in users_q]
                    except Exception:
                        roles_count = 0
                        users_by_role = []
                    return render_template('home_panel/struct.html', usuario=user, developer_priv=developer_priv, role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/manage_user.html', users=users, roles=roles, statuses=statuses, message='Error al actualizar el usuario', current_user_id=current_user_id)

    try:
        roles_count = Roles.query.count()
        users_q = db.session.query(Roles.nombre_rol, func.count(Usuarios.id_user)).join(Usuarios, Usuarios.id_rol == Roles.id_rol).group_by(Roles.id_rol).all()
        users_by_role = [{'role': r or 'Sin nombre', 'count': int(c)} for r, c in users_q]
    except Exception:
        roles_count = 0
        users_by_role = []

    return render_template('home_panel/struct.html', usuario=user, developer_priv=developer_priv, role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/manage_user.html', users=users, roles=roles, statuses=statuses, current_user_id=current_user_id)


def registro_persona_ext_view(pid, tipo):
    """Formulario de extensión para completar datos según tipo: estudiante, representante, profesor, empleado."""
    if 'user_id' not in session:
        return redirect(url_for('login.login_handler'))

    ctx = get_user_context(session)

    # comprobar que la persona exista
    try:
        p = db.session.execute(text('SELECT id_persona, primer_nombre, primer_apellido FROM personas WHERE id_persona = :pid'), {'pid': pid}).fetchone()
    except Exception:
        p = None

    if not p:
        return abort(404, 'Persona no encontrada')

    message = None

    # Estudiante
    if tipo == 'estudiante':
        if request.method == 'POST':
            fecha_inscripcion = request.form.get('fecha_inscripcion')
            try:
                db.session.execute(text('INSERT INTO estudiantes (id_persona, fecha_inscripcion) VALUES (:idp, :fins)'), {'idp': pid, 'fins': fecha_inscripcion})
                db.session.commit()
                message = 'Estudiante registrado correctamente'
                return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), content_template='home_panel/registro_ext_estudiante.html', persona=p, message=message)
            except Exception as e:
                db.session.rollback()
                message = f'Error: {str(e)}'

        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), content_template='home_panel/registro_ext_estudiante.html', persona=p, message=message)

    # Representante
    if tipo == 'representante':
        if request.method == 'POST':
            numero_hijos = request.form.get('numero_hijos') or 0
            id_profesion = request.form.get('id_profesion') or None
            id_ocupacion = request.form.get('id_ocupacion') or None
            try:
                db.session.execute(text('INSERT INTO representantes (id_persona, id_profesion, id_ocupacion, numero_hijos) VALUES (:idp, :prof, :ocu, :nh)'), {'idp': pid, 'prof': id_profesion, 'ocu': id_ocupacion, 'nh': int(numero_hijos)})
                db.session.commit()
                message = 'Representante registrado correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error: {str(e)}'

        # cargar selects
        try:
            profesiones = db.session.execute(text('SELECT id_profesion, nombre_profesion FROM profesiones')).fetchall()
        except Exception:
            profesiones = []
        try:
            ocupaciones = db.session.execute(text('SELECT id_ocupacion, nombre_ocupacion FROM ocupaciones')).fetchall()
        except Exception:
            ocupaciones = []

        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), content_template='home_panel/registro_ext_representante.html', persona=p, profesiones=profesiones, ocupaciones=ocupaciones, message=message)

    # Profesor
    if tipo == 'profesor':
        if request.method == 'POST':
            id_especialidad = request.form.get('id_especialidad') or None
            try:
                db.session.execute(text('INSERT INTO profesores (id_persona, id_especialidad) VALUES (:idp, :idesp)'), {'idp': pid, 'idesp': id_especialidad})
                db.session.commit()
                message = 'Profesor registrado correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error: {str(e)}'

        try:
            especialidades = db.session.execute(text('SELECT id_especialidad, nombre_especialidad FROM especialidades')).fetchall()
        except Exception:
            especialidades = []

        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), content_template='home_panel/registro_ext_profesor.html', persona=p, especialidades=especialidades, message=message)

    # Empleado
    if tipo == 'empleado':
        if request.method == 'POST':
            id_cargo = request.form.get('id_cargo') or None
            fecha_contratacion = request.form.get('fecha_contratacion') or None
            salario = request.form.get('salario') or None
            try:
                db.session.execute('INSERT INTO empleados (id_persona, id_cargo, fecha_contratacion, salario) VALUES (:idp, :idc, :fcont, :sal)', {'idp': pid, 'idc': id_cargo, 'fcont': fecha_contratacion, 'sal': salario})
                db.session.commit()
                message = 'Empleado registrado correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error: {str(e)}'

        try:
            cargos = db.session.execute('SELECT id_cargo, nombre_cargo FROM cargos').fetchall()
        except Exception:
            cargos = []

        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), content_template='home_panel/registro_ext_empleado.html', persona=p, cargos=cargos, message=message)

    return abort(404)


def developer_secciones_existentes_view():
    """Vista para ver secciones existentes (solo desarrolladores)."""
    ctx = get_user_context(session)
    if not ctx['developer_priv']:
        abort(403)

    try:
        secciones = db.session.execute(text('''
            SELECT s.id_seccion, g.numero_grado, l.letra, n.nombre_nivel
            FROM secciones s
            LEFT JOIN grados g ON s.id_grado = g.id_grado
            LEFT JOIN letra_seccion l ON s.id_letra_seccion = l.id_letra_seccion
            LEFT JOIN niveles n ON s.id_nivel = n.id_nivel
        ''')).fetchall()
    except Exception:
        secciones = []

    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=0, users_by_role=[], content_template='home_panel/developer_secciones_existentes.html', secciones=secciones)


def developer_import_export_view():
    """Vista para importar/exportar BD (solo desarrolladores)."""
    ctx = get_user_context(session)
    if not ctx['developer_priv']:
        abort(403)

    message = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'export':
            # Exportar BD a SQL
            try:
                if db.engine.name == 'sqlite':
                    import sqlite3
                    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                    conn = sqlite3.connect(db_path)
                    with open('backup.sql', 'w', encoding='utf-8') as f:
                        for line in conn.iterdump():
                            f.write('%s\n' % line)
                    conn.close()
                    message = 'BD exportada a backup.sql'
                elif db.engine.name == 'mysql':
                    # Para MySQL, usar mysqldump
                    import subprocess
                    DB_USER = os.getenv("DB_USER")
                    DB_PASS = os.getenv("DB_PASS")
                    DB_NAME = os.getenv("DB_NAME")
                    DB_HOST = os.getenv("DB_HOST", "localhost")
                    cmd = f"mysqldump -u {DB_USER} -p{DB_PASS} -h {DB_HOST} {DB_NAME} > backup.sql"
                    subprocess.run(cmd, shell=True)
                    message = 'BD exportada a backup.sql'
                else:
                    message = 'Engine no soportado'
            except Exception as e:
                message = f'Error al exportar: {str(e)}'
        elif action == 'import':
            # Importar desde archivo
            file = request.files.get('sql_file')
            if file:
                try:
                    sql_content = file.read().decode('utf-8')
                    if db.engine.name == 'sqlite':
                        import sqlite3
                        db_path = db.engine.url.database
                        conn = sqlite3.connect(db_path)
                        conn.executescript(sql_content)
                        conn.commit()
                        conn.close()
                        message = 'BD importada correctamente'
                    elif db.engine.name == 'mysql':
                        # Para MySQL, usar pymysql
                        import pymysql
                        DB_USER = os.getenv("DB_USER")
                        DB_PASS = os.getenv("DB_PASS")
                        DB_NAME = os.getenv("DB_NAME")
                        DB_HOST = os.getenv("DB_HOST", "localhost")
                        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
                        cursor = conn.cursor()
                        # Ejecutar statement por statement
                        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                        for stmt in statements:
                            if stmt:
                                cursor.execute(stmt)
                        conn.commit()
                        conn.close()
                        message = 'BD importada correctamente'
                    else:
                        message = 'Engine no soportado'
                except Exception as e:
                    message = f'Error al importar: {str(e)}'
            else:
                message = 'Selecciona un archivo SQL'

    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=0, users_by_role=[], content_template='home_panel/developer_import_export.html', message=message)
