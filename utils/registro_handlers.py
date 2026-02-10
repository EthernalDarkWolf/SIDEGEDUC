from flask import render_template, redirect, url_for, request, session, abort
from database.models import db
from sqlalchemy import text


def tipo_de_registro_persona(tipo, ctx, roles_count, users_by_role):
    """Manejador de registros movido a utils para mantener view_handlers más limpio.
    Recibe `ctx`, `roles_count` y `users_by_role` calculados por el wrapper.
    """
    allowed = [
        'plantel', 'personas', 'materias', 'secciones',
        'letra_seccion', 'grados', 'niveles', 'matriculas', 'personal_admin'
    ]
    if tipo not in allowed:
        return abort(404, 'Tipo de registro no válido')

    message = None

    # Personas (crear persona y redirigir a extensión según tipo)
    if tipo == 'personas':
        if request.method == 'POST':
            f = request.form
            primer = f.get('primer_nombre')
            segundo = f.get('segundo_nombre')
            pap = f.get('primer_apellido')
            sap = f.get('segundo_apellido')
            fecha_nac = f.get('fecha_nacimiento')
            tipo_persona = f.get('tipo_persona')
            id_sexo = f.get('id_sexo') or None
            id_tipo_doc = f.get('id_tipo_documento') or None
            numero_cedula = f.get('numero_cedula') or None

            if not primer or not pap or not fecha_nac or not tipo_persona:
                message = 'Campos requeridos faltantes.'
            else:
                # Prevención: si la cédula ya existe, evitar re-registrar
                try:
                    if numero_cedula:
                        existing = db.session.execute(text('SELECT id_persona FROM personas WHERE numero_cedula = :num'), {'num': numero_cedula}).fetchone()
                    else:
                        existing = None
                except Exception:
                    existing = None

                if existing:
                    message = 'Persona ya registrada. No puedes volver a registrarla.'
                else:
                    try:
                        insert_person = text(
                            'INSERT INTO personas '
                            '(primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, '
                            'fecha_nacimiento, id_sexo, tipo_persona, id_tipo_documento, numero_cedula) '
                            'VALUES (:primer, :segundo, :pap, :sap, :fecha, :id_sexo, :tipo_persona, :id_tipo_doc, :num_ced)'
                        )
                        db.session.execute(insert_person, {
                            'primer': primer,
                            'segundo': segundo or None,
                            'pap': pap,
                            'sap': sap or None,
                            'fecha': fecha_nac or None,
                            'id_sexo': id_sexo,
                            'tipo_persona': tipo_persona,
                            'id_tipo_doc': int(id_tipo_doc) if id_tipo_doc and id_tipo_doc.isdigit() else None,
                            'num_ced': numero_cedula or None
                        })
                        db.session.commit()

                        if db.engine.name == 'sqlite':
                            new_id = int(db.session.execute(text('SELECT last_insert_rowid()')).scalar() or 0)
                        else:
                            r = db.session.execute(text('SELECT LAST_INSERT_ID() as id')).fetchone()
                            new_id = int(r[0]) if r else 0

                        return redirect(url_for('registro_persona_ext', pid=new_id, tipo=tipo_persona))
                    except Exception as e:
                        db.session.rollback()
                        message = f'Error al registrar persona: {e}'

        # GET: carga selects necesarios
        try:
            sexos = db.session.execute(text('SELECT id_sexo, letra_sexo FROM sexo')).fetchall()
        except Exception:
            sexos = []
        try:
            tipo_documentos = db.session.execute(text('SELECT id_tipo_documento, nombre_tipo_documento FROM tipo_documento')).fetchall()
        except Exception:
            tipo_documentos = []

        return render_template(
            'home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'],
            role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'),
            roles_count=roles_count, users_by_role=users_by_role,
            content_template='home_panel/registro_persona_v2.html',
            sexos=sexos, tipo_documentos=tipo_documentos, message=message
        )

    # Plantel
    if tipo == 'plantel':
        if request.method == 'POST':
            f = request.form
            nombre = f.get('nombre_plantel_nomina')
            codigo_pa = f.get('codigo_pa')
            id_nivel = f.get('id_nivel') or None
            id_cargo = f.get('id_cargo') or None
            try:
                db.session.execute(
                    text('INSERT INTO planteles (codigo_pa, nombre_plantel_nomina, id_nivel, id_cargo) '
                         'VALUES (:codigo_pa, :nombre, :id_nivel, :id_cargo)')
                    , {'codigo_pa': codigo_pa, 'nombre': nombre, 'id_nivel': id_nivel, 'id_cargo': id_cargo}
                )
                db.session.commit()
                message = 'Plantel registrado correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error al registrar plantel: {e}'

        niveles = db.session.execute(text('SELECT id_nivel, nombre_nivel FROM niveles')).fetchall()
        cargos = db.session.execute(text('SELECT id_cargo, nombre_cargo FROM cargos')).fetchall()
        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'],
                               role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'),
                               roles_count=roles_count, users_by_role=users_by_role,
                               content_template='home_panel/registro_plantel.html', niveles=niveles, cargos=cargos, message=message)

    # Materias
    if tipo == 'materias':
        if request.method == 'POST':
            nombre_materia = request.form.get('nombre_materia')
            try:
                db.session.execute(text('INSERT INTO materias (nombre_materia) VALUES (:name)'), {'name': nombre_materia})
                db.session.commit()
                message = 'Materia creada correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error al crear materia: {e}'
        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'],
                               role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'),
                               roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_materias.html', message=message)

    # Secciones y acciones relacionadas
    if tipo == 'secciones':
        action = request.args.get('action')
        # manejar distintas acciones con bloques cortos
        if request.method == 'POST' and not action:
            f = request.form
            try:
                db.session.execute(text('INSERT INTO secciones (id_letra_seccion, id_grado, id_nivel) VALUES (:id_letra, :id_grado, :id_nivel)'),
                                   {'id_letra': f.get('id_letra_seccion') or None, 'id_grado': f.get('id_grado') or None, 'id_nivel': f.get('id_nivel') or None})
                db.session.commit()
                message = 'Sección creada correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error al crear sección: {e}'

        # acciones: add_student, assign_professor, assign_materia
        if request.args.get('action') == 'add_student':
            if request.method == 'POST':
                try:
                    db.session.execute(text('INSERT INTO estudiante_seccion (id_estudiante, id_seccion) VALUES (:est, :sec)'),
                                       {'est': request.form.get('id_estudiante'), 'sec': request.form.get('id_seccion')})
                    db.session.commit()
                    message = 'Estudiante asignado a sección correctamente'
                except Exception as e:
                    db.session.rollback()
                    message = f'Error: {e}'

        if request.args.get('action') == 'assign_professor':
            if request.method == 'POST':
                try:
                    db.session.execute(text('INSERT INTO profesor_seccion (id_profesor, id_seccion) VALUES (:prof, :sec)'),
                                       {'prof': request.form.get('id_profesor'), 'sec': request.form.get('id_seccion')})
                    db.session.commit()
                    message = 'Profesor asignado a sección correctamente'
                except Exception as e:
                    db.session.rollback()
                    message = f'Error: {e}'

        if request.args.get('action') == 'assign_materia':
            if request.method == 'POST':
                try:
                    db.session.execute(text('INSERT INTO materias_seccion (id_materia, id_seccion) VALUES (:mid, :sid)'),
                                       {'mid': request.form.get('id_materia'), 'sid': request.form.get('id_seccion')})
                    db.session.commit()
                    message = 'Materia asignada a sección correctamente'
                except Exception as e:
                    db.session.rollback()
                    message = f'Error: {e}'

        # cargar selects comunes
        estudiantes = db.session.execute(text('SELECT e.id_estudiante, p.primer_nombre, p.primer_apellido FROM estudiantes e JOIN personas p ON e.id_persona = p.id_persona')).fetchall()
        secciones = db.session.execute(text('SELECT id_seccion, id_grado, id_letra_seccion FROM secciones')).fetchall()
        profesores = db.session.execute(text('SELECT pr.id_profesor, p.primer_nombre, p.primer_apellido FROM profesores pr JOIN personas p ON pr.id_persona = p.id_persona')).fetchall()
        materias = db.session.execute(text('SELECT id_materia, nombre_materia FROM materias')).fetchall()

        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'],
                               role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'),
                               roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_secciones.html',
                               estudiantes=estudiantes, secciones=secciones, profesores=profesores, materias=materias, message=message)

    # Letras, grados, niveles (pequeños formularios)
    if tipo == 'letra_seccion':
        if request.method == 'POST':
            try:
                db.session.execute(text('INSERT INTO letra_seccion (letra) VALUES (:letra)'), {'letra': request.form.get('letra')})
                db.session.commit()
                message = 'Letra de sección creada correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error: {e}'
        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'],
                               role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'),
                               roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_tipo.html', tipo=tipo, title='Registro', message=message)

    if tipo == 'grados':
        if request.method == 'POST':
            try:
                db.session.execute(text('INSERT INTO grados (numero_grado) VALUES (:numero)'), {'numero': request.form.get('numero_grado')})
                db.session.commit()
                message = 'Grado creado correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error: {e}'
        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'],
                               role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'),
                               roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_tipo.html', tipo=tipo, title='Registro', message=message)

    if tipo == 'niveles':
        if request.method == 'POST':
            try:
                db.session.execute(text('INSERT INTO niveles (nombre_nivel) VALUES (:nombre)'), {'nombre': request.form.get('nombre_nivel')})
                db.session.commit()
                message = 'Nivel creado correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error: {e}'
        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'],
                               role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'),
                               roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_tipo.html', tipo=tipo, title='Registro', message=message)

    # Matrículas (nuevo sub-módulo simple)
    if tipo == 'matriculas':
        if request.method == 'POST':
            try:
                # placeholder: manejar POST para crear matrícula
                student_id = request.form.get('id_estudiante')
                section_id = request.form.get('id_seccion')
                db.session.execute(text('INSERT INTO matriculas (id_estudiante, id_seccion) VALUES (:est, :sec)'), {'est': student_id, 'sec': section_id})
                db.session.commit()
                message = 'Matrícula creada correctamente'
            except Exception as e:
                db.session.rollback()
                message = f'Error al crear matrícula: {e}'

        # cargar datos para el formulario
        try:
            estudiantes = db.session.execute(text('SELECT id_estudiante, id_persona FROM estudiantes')).fetchall()
        except Exception:
            estudiantes = []
        try:
            secciones = db.session.execute(text('SELECT id_seccion, id_grado, id_letra_seccion FROM secciones')).fetchall()
        except Exception:
            secciones = []
        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'],
                               role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'),
                               roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_matriculas.html', estudiantes=estudiantes, secciones=secciones, message=message)

    # Si no se matcheó, devolver plantilla por defecto
    return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'],
                           role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'),
                           roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_tipo.html', tipo=tipo, title='Registro')
