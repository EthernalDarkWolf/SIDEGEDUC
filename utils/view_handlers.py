"""Script manejador de las vistras del sistema
con sus respectivas funciones"""

from datetime import datetime
from flask import render_template, redirect, url_for, request, session, send_file
from database.models import Usuarios, Roles, StatusUser, db
from sqlalchemy import func, text
import io
from .permissions import get_user_context, user_has_admin_privileges
from flask import abort
import os
from werkzeug.security import check_password_hash, generate_password_hash


def compute_role_counts(ctx):
    """Devuelve (roles_count, users_by_role) respetando la visibilidad del rol 'Creador'.
    Si el usuario NO es creador, el rol 'Creador' se excluye de los conteos y listados.
    """
    try:
        if ctx.get('is_creator'):
            roles_count = Roles.query.count()
            users_q = db.session.query(Roles.nombre_rol, func.count(Usuarios.id_user)).join(Usuarios, Usuarios.id_rol == Roles.id_rol).group_by(Roles.id_rol).all()
        else:
            # Filtrar 'Creador' de forma insensible a mayúsculas y espacios
            roles_count = Roles.query.filter(func.lower(func.trim(Roles.nombre_rol)) != 'creador').count()
            users_q = db.session.query(Roles.nombre_rol, func.count(Usuarios.id_user)).join(Usuarios, Usuarios.id_rol == Roles.id_rol).filter(func.lower(func.trim(Roles.nombre_rol)) != 'creador').group_by(Roles.id_rol).all()
        users_by_role = [{'role': r or 'Sin nombre', 'count': int(c)} for r, c in users_q]
    except Exception:
        roles_count = 0
        users_by_role = []
    return roles_count, users_by_role


def home_panel():
    #Muestra la página principal del dashboard 
    ctx = get_user_context(session)
    # Conteos: total de roles y usuarios por rol (respetando visibilidad de 'Creador')
    roles_count, users_by_role = compute_role_counts(ctx)

    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role)


def login():
    #Ruta raíz; redirige al dashboard si hay sesión activa, al login si no
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login.login_handler'))


def boleta():
    return '<h2>La seccion Boletas esta en las ultimas etapas de desarrollo</h2>' \
           '<h2> En muy poco tiempo estara operativo... </h2>'

def constancia():
    # Mantener compatibilidad: redirigir a la nueva vista de consultas
    return consultas()


def consultas():
    """Vista de consultas: muestra conteos de personas, materias y secciones."""
    ctx = get_user_context(session)
    try:
        total_personas = db.session.execute(text('SELECT COUNT(*) FROM personas')).scalar() or 0
    except Exception:
        total_personas = 0
    try:
        total_materias = db.session.execute(text('SELECT COUNT(*) FROM materias')).scalar() or 0
    except Exception:
        total_materias = 0
    try:
        total_secciones = db.session.execute(text('SELECT COUNT(*) FROM secciones')).scalar() or 0
    except Exception:
        total_secciones = 0
    try:
        total_planteles = db.session.execute(text('SELECT COUNT(*) FROM planteles')).scalar() or 0
    except Exception:
        total_planteles = 0

    roles_count, users_by_role = compute_role_counts(ctx)

    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/consultas.html', total_personas=total_personas, total_materias=total_materias, total_secciones=total_secciones, total_planteles=total_planteles)


def consultas_personas():
    """Página de detalle para Personas: muestra mini-cuadros por rol (estudiante, profesor, representante, empleado)."""
    ctx = get_user_context(session)
    try:
        total_est = int(db.session.execute(text('SELECT COUNT(*) FROM estudiantes')).scalar() or 0)
    except Exception:
        total_est = 0
    try:
        total_prof = int(db.session.execute(text('SELECT COUNT(*) FROM profesores')).scalar() or 0)
    except Exception:
        total_prof = 0
    try:
        total_rep = int(db.session.execute(text('SELECT COUNT(*) FROM representantes')).scalar() or 0)
    except Exception:
        total_rep = 0
    try:
        total_emp = int(db.session.execute(text('SELECT COUNT(*) FROM empleados')).scalar() or 0)
    except Exception:
        total_emp = 0
    # Personas sin rol (no están en estudiantes/profesores/representantes/empleados)
    try:
        total_sinrol = int(db.session.execute(text('''
            SELECT COUNT(*) FROM personas p
            WHERE NOT EXISTS (SELECT 1 FROM estudiantes e WHERE e.id_persona = p.id_persona)
              AND NOT EXISTS (SELECT 1 FROM profesores pr WHERE pr.id_persona = p.id_persona)
              AND NOT EXISTS (SELECT 1 FROM representantes r WHERE r.id_persona = p.id_persona)
              AND NOT EXISTS (SELECT 1 FROM empleados em WHERE em.id_persona = p.id_persona)
        ''')).scalar() or 0)
    except Exception:
        total_sinrol = 0

    roles_count, users_by_role = compute_role_counts(ctx)

    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/consultas_personas.html', total_estudiantes=total_est, total_profesores=total_prof, total_representantes=total_rep, total_empleados=total_emp, total_sinrol=total_sinrol)


def consultas_personas_list():
    """Listado de personas por rol. Query param: role (estudiante|profesor|representante|empleado)"""
    ctx = get_user_context(session)
    role = request.args.get('role') or request.view_args.get('role') if request.view_args else request.args.get('role')
    role = (role or '').lower()
    rows = []
    role_display = ''
    title = ''
    try:
        if role == 'estudiante':
            rows = db.session.execute(text('''
                SELECT p.*, e.fecha_inscripcion, na.nombre_nivel_academico
                FROM estudiantes e
                JOIN personas p ON e.id_persona = p.id_persona
                LEFT JOIN niveles_academicos na ON na.id_nivel_academico = (
                    SELECT id_nivel_academico FROM representantes r WHERE r.id_persona = p.id_persona LIMIT 1
                )
            ''')).fetchall()
            role_display = 'Estudiante'
            title = 'Listado de Estudiantes'
        elif role == 'profesor' or role == 'profesores':
            rows = db.session.execute(text('''
                SELECT p.*, pr.id_profesor, es.nombre_especialidad
                FROM profesores pr
                JOIN personas p ON pr.id_persona = p.id_persona
                LEFT JOIN especialidades es ON pr.id_especialidad = es.id_especialidad
            ''')).fetchall()
            role_display = 'Profesor'
            title = 'Listado de Profesores'
        elif role == 'representante' or role == 'representantes':
            rows = db.session.execute(text('''
                SELECT p.*, r.id_representante, prf.nombre AS profesion, oc.nombre AS ocupacion, na.nombre_nivel_academico
                FROM representantes r
                JOIN personas p ON r.id_persona = p.id_persona
                LEFT JOIN profesiones prf ON r.id_profesion = prf.id
                LEFT JOIN ocupaciones oc ON r.id_ocupacion = oc.id
                LEFT JOIN niveles_academicos na ON r.id_nivel_academico = na.id_nivel_academico
            ''')).fetchall()
            role_display = 'Representante'
            title = 'Listado de Representantes'
        elif role == 'empleado' or role == 'empleados':
            rows = db.session.execute(text('''
                SELECT p.*, em.id_empleado, c.nombre_cargo, em.fecha_contratacion, em.salario
                FROM empleados em
                JOIN personas p ON em.id_persona = p.id_persona
                LEFT JOIN cargos c ON em.id_cargo = c.id_cargo
            ''')).fetchall()
            role_display = 'Empleado'
            title = 'Listado de Empleados'
        elif role == 'sinrol':
            # personas que no tienen ninguna fila de rol
            rows = db.session.execute(text('''
                SELECT p.* FROM personas p
                WHERE NOT EXISTS (SELECT 1 FROM estudiantes e WHERE e.id_persona = p.id_persona)
                  AND NOT EXISTS (SELECT 1 FROM profesores pr WHERE pr.id_persona = p.id_persona)
                  AND NOT EXISTS (SELECT 1 FROM representantes r WHERE r.id_persona = p.id_persona)
                  AND NOT EXISTS (SELECT 1 FROM empleados em WHERE em.id_persona = p.id_persona)
            ''')).fetchall()
            role_display = 'Sin rol'
            title = 'Personas sin rol'
    except Exception:
        rows = []

    roles_count, users_by_role = compute_role_counts(ctx)

    # si no se logró identificar un role_display, hacerlo genérico
    if not role_display:
        role_display = role.capitalize() if role else ''
    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/consultas_personas_list.html', rows=rows, role_display=role_display, title=title, role=role)


def editar_registro_persona():
    """Redirige al formulario de edición (reusa `registro_persona_ext_vista` para editar)."""
    if 'user_id' not in session:
        return redirect(url_for('login.login_handler'))
    pid = request.args.get('id')
    role = request.args.get('role')
    if not pid:
        return redirect(url_for('consultas_personas'))
    # Map role to tipo: estudiante->estudiante, profesor->profesor, representante->representante, empleado->empleado
    tipo = role
    try:
        pid_int = int(pid)
    except Exception:
        return redirect(url_for('consultas_personas'))
    # Reusar vista de edición/extension si existe
    return registro_persona_ext_vista(pid_int, tipo)


def editar_persona():
    """Editar datos básicos de una persona. GET: mostrar formulario prellenado. POST: actualizar la tabla `personas`.
    Usa la misma plantilla `registro_persona_v2.html` pero con `person` y `edit=True`.
    """
    if 'user_id' not in session:
        return redirect(url_for('login.login_handler'))

    pid = request.args.get('id') if request.method == 'GET' else request.form.get('id_persona')
    if not pid:
        return redirect(url_for('consultas_personas'))
    try:
        pid_int = int(pid)
    except Exception:
        return redirect(url_for('consultas_personas'))

    message = None
    # POST => actualizar
    if request.method == 'POST':
        f = request.form
        # validate names similar a registro (primera letra mayúscula, resto minúscula)
        def _cap_first(s):
            s = (s or '').strip()
            return s[0].upper() + s[1:].lower() if s else ''

        primer = _cap_first(f.get('primer_nombre'))
        segundo = _cap_first(f.get('segundo_nombre'))
        pap = _cap_first(f.get('primer_apellido'))
        sap = _cap_first(f.get('segundo_apellido'))
        if any(char.isdigit() for char in primer+segundo+pap+sap):
            message = 'Los nombres y apellidos no pueden contener números.'
        elif len(primer) > 20 or (segundo and len(segundo) > 20) or len(pap) > 20 or (sap and len(sap) > 20):
            message = 'Cada nombre o apellido debe tener como máximo 20 caracteres.'
        elif primer == pap or primer == sap or segundo == pap or segundo == sap:
            message = 'El nombre y los apellidos deben ser distintos entre sí.'
        elif segundo and segundo == primer:
            message = 'Primer nombre y segundo nombre no pueden ser iguales.'
        else:
            try:
                fecha = f.get('fecha_nacimiento') or None
                db.session.execute(text('''
                    UPDATE personas SET primer_nombre=:primer, segundo_nombre=:segundo, primer_apellido=:pap, segundo_apellido=:sap,
                    fecha_nacimiento=:fecha, id_sexo=:id_sexo, tipo_persona=:tipo_persona, id_tipo_documento=:id_tipo_doc, numero_cedula=:num_ced,
                    num_hijos=:num_hijos, id_relacion_familiar=:id_rel
                    WHERE id_persona = :idp
                '''), {
                    'primer': primer,
                    'segundo': segundo or None,
                    'pap': pap,
                    'sap': sap or None,
                    'fecha': fecha,
                    'id_sexo': f.get('id_sexo') or None,
                    'tipo_persona': f.get('tipo_persona'),
                    'id_tipo_doc': int(f.get('id_tipo_documento')) if f.get('id_tipo_documento') and str(f.get('id_tipo_documento')).isdigit() else None,
                    'num_ced': f.get('numero_cedula') or None,
                    'num_hijos': int(f.get('num_hijos')) if f.get('num_hijos') and str(f.get('num_hijos')).isdigit() else None,
                    'id_rel': int(f.get('id_relacion_familiar')) if f.get('id_relacion_familiar') and str(f.get('id_relacion_familiar')).isdigit() else None,
                    'idp': pid_int
                })
                db.session.commit()
                message = 'Persona actualizada correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error al actualizar persona: {e}'

        # después de editar, redirigir a la lista del rol si viene en el form
        # Intentar también actualizar/crear filas en tablas de rol según el tipo
        role = (f.get('role') or f.get('tipo_persona') or '').lower()
        try:
            if role == 'estudiante':
                fins = f.get('fecha_inscripcion') or None
                # si existe estudiante -> update, si no -> insert
                exists = db.session.execute(text('SELECT id_estudiante FROM estudiantes WHERE id_persona = :id'), {'id': pid_int}).fetchone()
                if exists:
                    db.session.execute(text('UPDATE estudiantes SET fecha_inscripcion = :f WHERE id_persona = :id'), {'f': fins, 'id': pid_int})
                else:
                    db.session.execute(text('INSERT INTO estudiantes (id_persona, fecha_inscripcion) VALUES (:id, :f)'), {'id': pid_int, 'f': fins})
            elif role == 'profesor':
                id_esp = f.get('id_especialidad') or None
                exists = db.session.execute(text('SELECT id_profesor FROM profesores WHERE id_persona = :id'), {'id': pid_int}).fetchone()
                if exists:
                    db.session.execute(text('UPDATE profesores SET id_especialidad = :idesp WHERE id_persona = :id'), {'idesp': id_esp, 'id': pid_int})
                else:
                    db.session.execute(text('INSERT INTO profesores (id_persona, id_especialidad) VALUES (:id, :idesp)'), {'id': pid_int, 'idesp': id_esp})
            elif role == 'representante':
                id_prof = f.get('id_profesion') or None
                id_ocu = f.get('id_ocupacion') or None
                id_niv = f.get('id_nivel_academico') or None
                exists = db.session.execute(text('SELECT id_representante FROM representantes WHERE id_persona = :id'), {'id': pid_int}).fetchone()
                if exists:
                    db.session.execute(text('UPDATE representantes SET id_profesion = :prof, id_ocupacion = :ocu, id_nivel_academico = :niv WHERE id_persona = :id'), {'prof': id_prof, 'ocu': id_ocu, 'niv': id_niv, 'id': pid_int})
                else:
                    db.session.execute(text('INSERT INTO representantes (id_persona, id_profesion, id_ocupacion, id_nivel_academico) VALUES (:id, :prof, :ocu, :niv)'), {'id': pid_int, 'prof': id_prof, 'ocu': id_ocu, 'niv': id_niv})
            elif role == 'empleado':
                id_cargo = f.get('id_cargo') or None
                fecha_cont = f.get('fecha_contratacion') or None
                salario = f.get('salario') or None
                exists = db.session.execute(text('SELECT id_empleado FROM empleados WHERE id_persona = :id'), {'id': pid_int}).fetchone()
                if exists:
                    db.session.execute(text('UPDATE empleados SET id_cargo = :idc, fecha_contratacion = :fcont, salario = :sal WHERE id_persona = :id'), {'idc': id_cargo, 'fcont': fecha_cont, 'sal': salario, 'id': pid_int})
                else:
                    db.session.execute(text('INSERT INTO empleados (id_persona, id_cargo, fecha_contratacion, salario) VALUES (:id, :idc, :fcont, :sal)'), {'id': pid_int, 'idc': id_cargo, 'fcont': fecha_cont, 'sal': salario})
            db.session.commit()
        except Exception:
            db.session.rollback()

        if role:
            return redirect(url_for('consultas_personas_list') + f'?role={role}')
        return redirect(url_for('consultas_personas'))

    # GET: cargar persona y selects
    try:
        p = db.session.execute(text('SELECT id_persona, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, fecha_nacimiento, id_sexo, id_tipo_documento, numero_cedula, num_hijos, id_relacion_familiar, tipo_persona FROM personas WHERE id_persona = :pid'), {'pid': pid_int}).fetchone()
    except Exception:
        p = None

    if not p:
        return redirect(url_for('consultas_personas'))

    # fetch selects
    try:
        sexos = db.session.execute(text('SELECT id_sexo, letra_sexo FROM sexo')).fetchall()
    except Exception:
        sexos = []
    try:
        tipo_documentos = db.session.execute(text('SELECT id_tipo_documento, nombre_tipo_documento FROM tipo_documento')).fetchall()
    except Exception:
        tipo_documentos = []

    # construir diccionario simple para template
    person = {
        'id_persona': p[0],
        'primer_nombre': p[1],
        'segundo_nombre': p[2],
        'primer_apellido': p[3],
        'segundo_apellido': p[4],
        'fecha_nacimiento': str(p[5]) if p[5] is not None else None,
        'id_sexo': p[6],
        'id_tipo_documento': p[7],
        'numero_cedula': p[8],
        'num_hijos': p[9],
        'id_relacion_familiar': p[10],
        'tipo_persona': p[11]
    }

    # Datos adicionales según rol (para prellenar formulario de edición)
    try:
        if person['tipo_persona'] == 'representante':
            rep = db.session.execute(text('SELECT id_profesion, id_ocupacion, id_nivel_academico FROM representantes WHERE id_persona = :pid'), {'pid': pid_int}).fetchone()
            if rep:
                person['id_profesion'] = rep[0]
                person['id_ocupacion'] = rep[1]
                person['id_nivel_academico'] = rep[2]
        elif person['tipo_persona'] == 'estudiante':
            est = db.session.execute(text('SELECT fecha_inscripcion FROM estudiantes WHERE id_persona = :pid'), {'pid': pid_int}).fetchone()
            if est:
                person['fecha_inscripcion'] = str(est[0]) if est[0] else None
        elif person['tipo_persona'] == 'profesor':
            prof = db.session.execute(text('SELECT id_especialidad FROM profesores WHERE id_persona = :pid'), {'pid': pid_int}).fetchone()
            if prof:
                person['id_especialidad'] = prof[0]
        elif person['tipo_persona'] == 'empleado':
            emp = db.session.execute(text('SELECT id_cargo, fecha_contratacion, salario FROM empleados WHERE id_persona = :pid'), {'pid': pid_int}).fetchone()
            if emp:
                person['id_cargo'] = emp[0]
                person['fecha_contratacion'] = str(emp[1]) if emp[1] else None
                person['salario'] = emp[2]
    except Exception:
        pass

    # Listas de apoyo para selects
    try:
        ocupaciones = db.session.execute(text('SELECT id, nombre FROM ocupaciones')).fetchall()
    except Exception:
        ocupaciones = []
    try:
        profesiones = db.session.execute(text('SELECT id, nombre FROM profesiones')).fetchall()
    except Exception:
        profesiones = []
    try:
        niveles_academicos = db.session.execute(text('SELECT id_nivel_academico, nombre_nivel_academico FROM niveles_academicos')).fetchall()
    except Exception:
        niveles_academicos = []
    try:
        especialidades = db.session.execute(text('SELECT id_especialidad, nombre_especialidad FROM especialidades')).fetchall()
    except Exception:
        especialidades = []
    try:
        cargos = db.session.execute(text('SELECT id_cargo, nombre_cargo FROM cargos')).fetchall()
    except Exception:
        cargos = []
    try:
        relaciones_familiares = db.session.execute(text('SELECT id, nombre FROM relaciones_familiares')).fetchall()
    except Exception:
        relaciones_familiares = []

    roles_count, users_by_role = compute_role_counts(get_user_context(session))

    return render_template('home_panel/struct.html', usuario=get_user_context(session)['user'], developer_priv=get_user_context(session)['developer_priv'], role_name=get_user_context(session).get('role_name'), role_desc=get_user_context(session).get('role_desc'), status=get_user_context(session).get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_persona_v2.html', sexos=sexos, tipo_documentos=tipo_documentos, person=person, edit=True, message=message, ocupaciones=ocupaciones, profesiones=profesiones, niveles_academicos=niveles_academicos, especialidades=especialidades, cargos=cargos, relaciones_familiares=relaciones_familiares)


def borrar_registro_persona():
    if 'user_id' not in session:
        return redirect(url_for('login.login_handler'))
    pid = request.form.get('id')
    role = (request.form.get('role') or '').lower()
    if not pid:
        return redirect(url_for('consultas_personas'))
    try:
        pid_int = int(pid)
    except Exception:
        return redirect(url_for('consultas_personas'))

    try:
        # Eliminar referencias dependientes de forma segura
        # borrar relaciones con secciones si existen
        try:
            db.session.execute(text('DELETE FROM estudiante_seccion WHERE id_estudiante IN (SELECT id_estudiante FROM estudiantes WHERE id_persona = :id)'), {'id': pid_int})
        except Exception:
            pass
        try:
            db.session.execute(text('DELETE FROM profesor_seccion WHERE id_profesor IN (SELECT id_profesor FROM profesores WHERE id_persona = :id)'), {'id': pid_int})
        except Exception:
            pass
        try:
            db.session.execute(text('DELETE FROM materias_seccion WHERE id_seccion IN (SELECT id_seccion FROM secciones WHERE id_seccion IN (SELECT id_seccion FROM secciones))'))
        except Exception:
            pass

        # eliminar fila en la tabla de rol
        if role == 'estudiante':
            db.session.execute(text('DELETE FROM estudiantes WHERE id_persona = :id'), {'id': pid_int})
        elif role == 'profesor':
            db.session.execute(text('DELETE FROM profesores WHERE id_persona = :id'), {'id': pid_int})
        elif role == 'representante':
            db.session.execute(text('DELETE FROM representantes WHERE id_persona = :id'), {'id': pid_int})
        elif role == 'empleado':
            db.session.execute(text('DELETE FROM empleados WHERE id_persona = :id'), {'id': pid_int})

        # eliminar association usuario-persona si existe
        try:
            db.session.execute(text('DELETE FROM usuario_persona WHERE id_persona = :id'), {'id': pid_int})
        except Exception:
            pass

        # eliminar entrada alternativa de cédula si existe
        try:
            db.session.execute(text('DELETE FROM persona_cedula WHERE id_persona = :id'), {'id': pid_int})
        except Exception:
            pass

        # finalmente eliminar la persona si ya no tiene dependencias
        try:
            db.session.execute(text('DELETE FROM personas WHERE id_persona = :id'), {'id': pid_int})
        except Exception:
            # si no se puede eliminar por FK, ignorar
            pass

        db.session.commit()
    except Exception:
        db.session.rollback()

    return redirect(url_for('consultas_personas'))


def consultas_materias():
    ctx = get_user_context(session)
    try:
        materias = db.session.execute(text('SELECT id_materia, nombre_materia FROM materias')).fetchall()
    except Exception:
        materias = []
    roles_count, users_by_role = compute_role_counts(ctx)
    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/consultas_materias.html', rows=materias, title='Listado de Materias')
def consultas_planteles():
    ctx = get_user_context(session)
    try:
        planteles = db.session.execute(text('SELECT id_plantel, nombre_plantel_nomina, codigo_pa FROM planteles')).fetchall()
    except Exception:
        planteles = []
    roles_count, users_by_role = compute_role_counts(ctx)
    # Refuerzo: asegurar que siempre se use la plantilla correcta y evitar duplicados
    return render_template(
        'home_panel/struct.html',
        usuario=ctx['user'],
        developer_priv=ctx['developer_priv'],
        role_name=ctx.get('role_name'),
        role_desc=ctx.get('role_desc'),
        status=ctx.get('status'),
        roles_count=roles_count,
        users_by_role=users_by_role,
        content_template='home_panel/consultas_planteles.html',
        rows=planteles,
        title='Listado de Planteles'
    )

def consultas_secciones():
    ctx = get_user_context(session)
    try:
        secciones = db.session.execute(text('SELECT id_seccion, id_grado, id_letra_seccion FROM secciones')).fetchall()
    except Exception:
        secciones = []
    roles_count, users_by_role = compute_role_counts(ctx)
    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/consultas_secciones.html', rows=secciones, title='Listado de Secciones')


def consultas_materias_editar():
    """Editar o crear materia desde la interfaz de consultas.
    GET: mostrar formulario con nombre prellenado si id proporcionado
    POST: crear o actualizar materia y redirigir al listado
    """
    if 'user_id' not in session:
        return redirect(url_for('login.login_handler'))
    ctx = get_user_context(session)
    if request.method == 'POST':
        mid = request.form.get('id_materia')
        name = request.form.get('nombre_materia')
        try:
            if mid:
                db.session.execute(text('UPDATE materias SET nombre_materia = :name WHERE id_materia = :id'), {'name': name, 'id': mid})
            else:
                db.session.execute(text('INSERT INTO materias (nombre_materia) VALUES (:name)'), {'name': name})
            db.session.commit()
        except Exception:
            db.session.rollback()
        return redirect(url_for('consultas_materias'))

    # GET
    mid = request.args.get('id')
    materia = None
    if mid:
        try:
            m = db.session.execute(text('SELECT id_materia, nombre_materia FROM materias WHERE id_materia = :id'), {'id': mid}).fetchone()
            if m:
                materia = {'id_materia': m[0], 'nombre_materia': m[1]}
        except Exception:
            materia = None

    roles_count, users_by_role = compute_role_counts(ctx)
    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_materias.html', materia=materia, edit=bool(materia))


def consultas_materias_borrar():
    if 'user_id' not in session:
        return redirect(url_for('login.login_handler'))
    mid = request.form.get('id')
    if not mid:
        return redirect(url_for('consultas_materias'))
    try:
        db.session.execute(text('DELETE FROM materias WHERE id_materia = :id'), {'id': mid})
        db.session.commit()
    except Exception:
        db.session.rollback()
    return redirect(url_for('consultas_materias'))


def consultas_secciones():
    # reutilizar query de developer_secciones_existentes_vista
    ctx = get_user_context(session)
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
    roles_count, users_by_role = compute_role_counts(ctx)
    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/developer_secciones_existentes.html', secciones=secciones)


def reporte_pdf_personas():
    """Genera y descarga PDF del listado de personas según rol."""
    if 'user_id' not in session:
        return redirect(url_for('login.login_handler'))
    role = (request.args.get('role') or '').lower()
    rows, role_display, title = [], '', 'Listado de Personas'
    try:
        if role == 'estudiante':
            rows = db.session.execute(text('''
                SELECT p.*, e.fecha_inscripcion, na.nombre_nivel_academico
                FROM estudiantes e JOIN personas p ON e.id_persona = p.id_persona
                LEFT JOIN niveles_academicos na ON na.id_nivel_academico = (SELECT id_nivel_academico FROM representantes r WHERE r.id_persona = p.id_persona LIMIT 1)
            ''')).fetchall()
            role_display, title = 'Estudiante', 'Listado de Estudiantes'
        elif role in ('profesor', 'profesores'):
            rows = db.session.execute(text('SELECT p.*, pr.id_profesor, es.nombre_especialidad FROM profesores pr JOIN personas p ON pr.id_persona = p.id_persona LEFT JOIN especialidades es ON pr.id_especialidad = es.id_especialidad')).fetchall()
            role_display, title = 'Profesor', 'Listado de Profesores'
        elif role in ('representante', 'representantes'):
            rows = db.session.execute(text('SELECT p.*, r.id_representante, prf.nombre AS profesion, oc.nombre AS ocupacion, na.nombre_nivel_academico FROM representantes r JOIN personas p ON r.id_persona = p.id_persona LEFT JOIN profesiones prf ON r.id_profesion = prf.id LEFT JOIN ocupaciones oc ON r.id_ocupacion = oc.id LEFT JOIN niveles_academicos na ON r.id_nivel_academico = na.id_nivel_academico')).fetchall()
            role_display, title = 'Representante', 'Listado de Representantes'
        elif role in ('empleado', 'empleados'):
            rows = db.session.execute(text('SELECT p.*, em.id_empleado, c.nombre_cargo, em.fecha_contratacion, em.salario FROM empleados em JOIN personas p ON em.id_persona = p.id_persona LEFT JOIN cargos c ON em.id_cargo = c.id_cargo')).fetchall()
            role_display, title = 'Empleado', 'Listado de Empleados'
        elif role == 'sinrol':
            rows = db.session.execute(text('SELECT p.* FROM personas p WHERE NOT EXISTS (SELECT 1 FROM estudiantes e WHERE e.id_persona = p.id_persona) AND NOT EXISTS (SELECT 1 FROM profesores pr WHERE pr.id_persona = p.id_persona) AND NOT EXISTS (SELECT 1 FROM representantes r WHERE r.id_persona = p.id_persona) AND NOT EXISTS (SELECT 1 FROM empleados em WHERE em.id_persona = p.id_persona)')).fetchall()
            role_display, title = 'Sin rol', 'Personas sin rol'
    except Exception:
        rows = []
    from .report_pdf import generar_pdf_personas
    pdf_bytes, err = generar_pdf_personas(rows, role_display, title)
    if err:
        return err, 500
    filename = f"reporte_personas_{role or 'todos'}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf', as_attachment=True, download_name=filename)


def reporte_pdf_planteles():
    """Genera y descarga PDF del listado de planteles."""
    if 'user_id' not in session:
        return redirect(url_for('login.login_handler'))
    try:
        rows = db.session.execute(text('SELECT id_plantel, nombre_plantel_nomina, codigo_pa FROM planteles')).fetchall()
    except Exception:
        rows = []
    from .report_pdf import generar_pdf_planteles
    pdf_bytes, err = generar_pdf_planteles(rows)
    if err:
        return err, 500
    filename = f"reporte_planteles_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf', as_attachment=True, download_name=filename)


def reporte_pdf_secciones():
    """Genera y descarga PDF del listado de secciones."""
    if 'user_id' not in session:
        return redirect(url_for('login.login_handler'))
    try:
        rows = db.session.execute(text('SELECT s.id_seccion, g.numero_grado, l.letra, n.nombre_nivel FROM secciones s LEFT JOIN grados g ON s.id_grado = g.id_grado LEFT JOIN letra_seccion l ON s.id_letra_seccion = l.id_letra_seccion LEFT JOIN niveles n ON s.id_nivel = n.id_nivel')).fetchall()
    except Exception:
        rows = []
    from .report_pdf import generar_pdf_secciones
    pdf_bytes, err = generar_pdf_secciones(rows)
    if err:
        return err, 500
    filename = f"reporte_secciones_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf', as_attachment=True, download_name=filename)



def consultas_planteles_editar():
    if 'user_id' not in session:
        return redirect(url_for('login.login_handler'))
    ctx = get_user_context(session)
    if request.method == 'POST':
        pid = request.form.get('id_plantel')
        nombre = request.form.get('nombre_plantel_nomina')
        codigo = request.form.get('codigo_pa')
        try:
            if pid:
                db.session.execute(text('UPDATE planteles SET nombre_plantel_nomina = :nom, codigo_pa = :cod WHERE id_plantel = :id'), {'nom': nombre, 'cod': codigo, 'id': pid})
            else:
                db.session.execute(text('INSERT INTO planteles (codigo_pa, nombre_plantel_nomina) VALUES (:codigo_pa, :nombre)'), {'codigo_pa': codigo, 'nombre': nombre})
            db.session.commit()
        except Exception:
            db.session.rollback()
        return redirect(url_for('consultas_planteles'))

    pid = request.args.get('id')
    plantel = None

    if pid:
        try:
            p = db.session.execute(text('SELECT id_plantel, nombre_plantel_nomina, codigo_pa FROM planteles WHERE id_plantel = :id'), {'id': pid}).fetchone()
            if p:
                plantel = {'id_plantel': p[0], 'nombre_plantel_nomina': p[1], 'codigo_pa': p[2]}
        except Exception:
            plantel = None

    roles_count, users_by_role = compute_role_counts(ctx)
    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_plantel.html', plantel=plantel, edit=bool(plantel))


def consultas_planteles_borrar():
    if 'user_id' not in session:
        return redirect(url_for('login.login_handler'))
    pid = request.form.get('id')
    if not pid:
        return redirect(url_for('consultas_planteles'))
    try:
        db.session.execute(text('DELETE FROM planteles WHERE id_plantel = :id'), {'id': pid})
        db.session.commit()
    except Exception:
        db.session.rollback()
    return redirect(url_for('consultas_planteles'))


def admin_alumnos():
    return 'Administración de alumnos - en desarrollo'


def usuarios_roles_registrados():
    #Lista de registros — reutiliza el contexto de usuario para permisos
    ctx = get_user_context(session)
    # Conteos: total de roles y usuarios por rol 
    roles_count, users_by_role = compute_role_counts(ctx)

    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registros.html')


def tipo_de_registro_persona(tipo):
    if 'user_id' not in session:
        return redirect(url_for('login.login_handler'))
    from . import registro_handlers as rh

    ctx = get_user_context(session)
    roles_count, users_by_role = compute_role_counts(ctx)

    return rh.tipo_de_registro_persona(
        tipo=tipo,
        ctx=ctx,
        roles_count=roles_count,
        users_by_role=users_by_role
    )


def administrador_herramientas():
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
    ctx = get_user_context(session)
    users = Usuarios.query.filter(Usuarios.id_user != cur.id_user).order_by(Usuarios.nombre).all()
    # Mostrar el rol 'Creador' solo al propio creador
    if ctx.get('is_creator'):
        roles = Roles.query.order_by(Roles.nombre_rol).all()
    else:
        # Excluir el rol 'Creador' (insensible a mayúsculas/espacios)
        roles = Roles.query.filter(func.lower(func.trim(Roles.nombre_rol)) != 'creador').order_by(Roles.nombre_rol).all()
    statuses = StatusUser.query.order_by(StatusUser.estado).all()
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
                    # Prevención: no permitir asignar el rol 'Creador' si el actor no es el creador
                    if new_role:
                        try:
                            role_obj = Roles.query.filter_by(id_rol=int(new_role)).first()
                        except Exception:
                            role_obj = None
                        if role_obj and (role_obj.nombre_rol or '').lower().replace(' ', '') == 'creador' and not ctx.get('is_creator'):
                            raise PermissionError('No autorizado para asignar el rol Creador')
                        target_user.id_rol = int(new_role)
                    if new_status:
                        target_user.id_status_user = int(new_status)
                    db.session.commit()
                    roles_count, users_by_role = compute_role_counts(ctx)
                    return render_template('home_panel/struct.html', usuario=user, developer_priv=developer_priv, role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/manage_user.html', users=users, roles=roles, statuses=statuses, message='Usuario actualizado correctamente', current_user_id=current_user_id, is_creator=ctx.get('is_creator'))
                except Exception:
                    db.session.rollback()
                    roles_count, users_by_role = compute_role_counts(ctx)
                    return render_template('home_panel/struct.html', usuario=user, developer_priv=developer_priv, role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/manage_user.html', users=users, roles=roles, statuses=statuses, message='Error al actualizar el usuario', current_user_id=current_user_id, is_creator=ctx.get('is_creator'))

    roles_count, users_by_role = compute_role_counts(ctx)

    return render_template('home_panel/struct.html', usuario=user, developer_priv=developer_priv, role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/manage_user.html', users=users, roles=roles, statuses=statuses, current_user_id=current_user_id, is_creator=ctx.get('is_creator'))


def registro_persona_ext_vista(pid, tipo):
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
            id_profesion = request.form.get('id_profesion') or None
            id_ocupacion = request.form.get('id_ocupacion') or None
            try:
                db.session.execute(text('INSERT INTO representantes (id_persona, id_profesion, id_ocupacion) VALUES (:idp, :prof, :ocu)'), {'idp': pid, 'prof': id_profesion, 'ocu': id_ocupacion})
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


def developer_secciones_existentes_vista():
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


def api_create_ocupacion():
    """API simple para crear una ocupación y devolver id/json."""
    try:
        data = request.get_json() or {}
        nombre = (data.get('nombre') or '').strip()
        if not nombre:
            return {'success': False, 'error': 'Nombre vacío'}
        # comprobar existencia
        existing = db.session.execute(text('SELECT id_ocupacion FROM ocupaciones WHERE LOWER(nombre_ocupacion)=LOWER(:n)'), {'n': nombre}).fetchone()
        if existing:
            return {'success': True, 'id': existing[0], 'nombre': nombre}
        # insertar
        db.session.execute(text('INSERT INTO ocupaciones (nombre_ocupacion) VALUES (:n)'), {'n': nombre})
        db.session.commit()
        # obtener id
        if db.engine.name == 'sqlite':
            nid = int(db.session.execute(text('SELECT last_insert_rowid()')).scalar() or 0)
        else:
            r = db.session.execute(text('SELECT LAST_INSERT_ID()')).fetchone(); nid = int(r[0]) if r else 0
        return {'success': True, 'id': nid, 'nombre': nombre}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}


def api_create_profesion():
    """Crear profesión (POST JSON {nombre}) y devolver id/json."""
    try:
        data = request.get_json() or {}
        nombre = (data.get('nombre') or '').strip()
        if not nombre:
            return {'success': False, 'error': 'Nombre vacío'}
        existing = db.session.execute(text('SELECT id_profesion FROM profesiones WHERE LOWER(nombre_profesion)=LOWER(:n)'), {'n': nombre}).fetchone()
        if existing:
            return {'success': True, 'id': existing[0], 'nombre': nombre}
        db.session.execute(text('INSERT INTO profesiones (nombre_profesion) VALUES (:n)'), {'n': nombre})
        db.session.commit()
        if db.engine.name == 'sqlite':
            nid = int(db.session.execute(text('SELECT last_insert_rowid()')).scalar() or 0)
        else:
            r = db.session.execute(text('SELECT LAST_INSERT_ID()')).fetchone(); nid = int(r[0]) if r else 0
        return {'success': True, 'id': nid, 'nombre': nombre}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}


def api_lookup_persona_by_cedula():
    """Buscar persona por numero de cédula (JSON)."""
    numero = request.args.get('numero') or ''
    numero = numero.strip()
    if not numero:
        return {'found': False}
    try:
        p = db.session.execute(text('SELECT id_persona, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, fecha_nacimiento, id_sexo, id_tipo_documento, numero_cedula, tipo_persona FROM personas WHERE numero_cedula = :num'), {'num': numero}).fetchone()
        if p:
            idp = p[0]
            # comprobar si ya tiene registros extendidos (estudiante, representante, profesor, empleado)
            est = db.session.execute(text('SELECT fecha_inscripcion FROM estudiantes WHERE id_persona = :idp'), {'idp': idp}).fetchone()
            rep = db.session.execute(text('SELECT 1 FROM representantes WHERE id_persona = :idp'), {'idp': idp}).fetchone()
            prof = db.session.execute(text('SELECT 1 FROM profesores WHERE id_persona = :idp'), {'idp': idp}).fetchone()
            emp = db.session.execute(text('SELECT 1 FROM empleados WHERE id_persona = :idp'), {'idp': idp}).fetchone()
            return {
                'found': True,
                'id': idp,
                'primer_nombre': p[1],
                'segundo_nombre': p[2],
                'primer_apellido': p[3],
                'segundo_apellido': p[4],
                'fecha_nacimiento': str(p[5]) if p[5] is not None else None,
                'id_sexo': p[6],
                'id_tipo_documento': p[7],
                'numero_cedula': p[8],
                'tipo_persona': p[9],
                'roles': {
                    'estudiante': bool(est),
                    'representante': bool(rep),
                    'profesor': bool(prof),
                    'empleado': bool(emp)
                },
                'fecha_inscripcion': str(est[0]) if est and est[0] is not None else None
            }
        # fallback: persona_cedula table si existe
        try:
            r = db.session.execute(text('SELECT pc.id_persona, p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido, p.fecha_nacimiento, p.id_sexo, p.id_tipo_documento, pc.numero_cedula, p.tipo_persona FROM persona_cedula pc JOIN personas p ON pc.id_persona = p.id_persona WHERE pc.numero_cedula = :num'), {'num': numero}).fetchone()
            if r:
                idp = r[0]
                est = db.session.execute(text('SELECT fecha_inscripcion FROM estudiantes WHERE id_persona = :idp'), {'idp': idp}).fetchone()
                rep = db.session.execute(text('SELECT 1 FROM representantes WHERE id_persona = :idp'), {'idp': idp}).fetchone()
                prof = db.session.execute(text('SELECT 1 FROM profesores WHERE id_persona = :idp'), {'idp': idp}).fetchone()
                emp = db.session.execute(text('SELECT 1 FROM empleados WHERE id_persona = :idp'), {'idp': idp}).fetchone()
                return {
                    'found': True,
                    'id': idp,
                    'primer_nombre': r[1],
                    'segundo_nombre': r[2],
                    'primer_apellido': r[3],
                    'segundo_apellido': r[4],
                    'fecha_nacimiento': str(r[5]) if r[5] is not None else None,
                    'id_sexo': r[6],
                    'id_tipo_documento': r[7],
                    'numero_cedula': r[8],
                    'tipo_persona': r[9],
                    'roles': {
                        'estudiante': bool(est),
                        'representante': bool(rep),
                        'profesor': bool(prof),
                        'empleado': bool(emp)
                    },
                    'fecha_inscripcion': str(est[0]) if est and est[0] is not None else None
                }
        except Exception:
            pass
        return {'found': False}
    except Exception:
        return {'found': False}


def developer_import_export_vista():
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


def configuracion_de_usuario():
    """Configuración de usuario: cambiar nombre, contraseña, borrar cuenta."""
    if 'user_id' not in session:
        return redirect(url_for('login.login_handler'))

    ctx = get_user_context(session)
    uid = ctx.get('current_user_id')
    user_obj = Usuarios.query.filter_by(id_user=uid).first()
    if not user_obj:
        return redirect(url_for('login.login_handler'))

    message = None
    message_type = 'info'

    if request.method == 'POST':
        action = request.form.get('action')
        try:
            if action == 'change_name':
                new_name = (request.form.get('new_name') or '').strip()
                if not new_name:
                    raise ValueError('El nombre no puede estar vacío')
                # comprobar unicidad
                exists = Usuarios.query.filter(Usuarios.nombre == new_name, Usuarios.id_user != user_obj.id_user).first()
                if exists:
                    raise ValueError('El nombre de usuario ya está en uso')
                user_obj.nombre = new_name
                db.session.commit()
                message = 'Nombre actualizado correctamente'
                message_type = 'success'

            elif action == 'change_password':
                current = request.form.get('current_password') or ''
                newpw = request.form.get('new_password') or ''
                confirm = request.form.get('confirm_password') or ''
                if not current or not newpw or not confirm:
                    raise ValueError('Completa todos los campos de contraseña')
                if newpw != confirm:
                    raise ValueError('Las nuevas contraseñas no coinciden')
                stored = user_obj.contrasena
                if not (check_password_hash(stored, current) or stored == current):
                    raise ValueError('Contraseña actual incorrecta')
                user_obj.contrasena = generate_password_hash(newpw)
                db.session.commit()
                message = 'Contraseña actualizada correctamente'
                message_type = 'success'

            elif action == 'delete_account':
                pw = request.form.get('confirm_password_delete') or ''
                if not pw:
                    raise ValueError('Debes indicar la contraseña para eliminar la cuenta')
                stored = user_obj.contrasena
                if not (check_password_hash(stored, pw) or stored == pw):
                    raise ValueError('Contraseña incorrecta')
                # eliminar usuario
                db.session.delete(user_obj)
                db.session.commit()
                session.clear()
                # mostrar modal en login informando del borrado
                return render_template('login/index.html', modal_show=True, modal_title='Usuario borrado', modal_message='Usuario borrado exitosamente', active='login', redirect_after_modal=True)
        except Exception as e:
            db.session.rollback()
            message = str(e)
            message_type = 'danger'

    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'], role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'), roles_count=0, users_by_role=[], content_template='home_panel/user_settings.html', message=message, message_type=message_type)


# Alias para compatibilidad con rutas que esperan el nombre `user_settings_vista`
def user_settings_vista():
    return configuracion_de_usuario()
