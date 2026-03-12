from flask import render_template, redirect, url_for, request, session, abort
from database.models import db
from sqlalchemy import text
from datetime import date


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
    def _cap_first(s):
        s = (s or '').strip()
        if not s:
            return ''
        return s[0].upper() + s[1:].lower()

    if tipo == 'personas':
        if request.method == 'POST':
            f = request.form
            # normalizar entradas (primera letra mayúscula, resto minúscula)
            primer = _cap_first(f.get('primer_nombre'))
            segundo = _cap_first(f.get('segundo_nombre'))
            pap = _cap_first(f.get('primer_apellido'))
            sap = _cap_first(f.get('segundo_apellido'))
            fecha_nac = (f.get('fecha_nacimiento') or '').strip()
            id_tipo_persona = int(f.get('id_tipo_persona') or 0)
            id_sexo = f.get('id_sexo') or None
            id_tipo_doc = f.get('id_tipo_documento') or None
            numero_cedula = (f.get('numero_cedula') or '').strip()
            id_ocupacion = int(f.get('id_ocupacion') or 0) if f.get('id_ocupacion') else None
            id_profesion = int(f.get('id_profesion') or 0) if f.get('id_profesion') else None
            num_hijos = int(f.get('num_hijos') or 0) if f.get('num_hijos') else None
            id_relacion_familiar = int(f.get('id_relacion_familiar') or 0) if f.get('id_relacion_familiar') else None

            # validaciones iniciales
            # básicos de cédula y tipo
            if not numero_cedula or not primer or not pap or not fecha_nac or not tipo_persona:
                message = 'Campos requeridos faltantes. Asegúrese de ingresar cédula, nombres, apellidos, fecha de nacimiento y tipo de persona.'
            elif not numero_cedula.isdigit():
                message = 'La cédula debe contener solo dígitos.'
            elif len(numero_cedula) < 7 or len(numero_cedula) > 9:
                message = 'La cédula debe tener entre 7 y 9 dígitos.'
            elif tipo_persona not in ['estudiante','profesor','representante','empleado']:
                message = 'Tipo de persona inválido.'
            # reglas de nombres
            elif any(char.isdigit() for char in primer+segundo+pap+sap):
                message = 'Los nombres y apellidos no pueden contener números.'
            elif len(primer) < 5 or len(primer) > 10 or (segundo and (len(segundo) < 5 or len(segundo) > 10)) or len(pap) < 5 or len(pap) > 10 or (sap and (len(sap) < 5 or len(sap) > 10)):
                message = 'Los nombres y apellidos deben tener entre 5 y 10 caracteres.'
            elif primer == pap or primer == sap or segundo == pap or segundo == sap:
                message = 'El nombre y los apellidos deben ser distintos entre sí.'
            elif segundo and segundo == primer:
                message = 'Primer nombre y segundo nombre no pueden ser iguales.'
            else:
                # Validaciones adicionales: fecha nacimiento no puede ser hoy ni en el futuro
                try:
                    y, m, d = map(int, fecha_nac.split('-'))
                    dob = date(y, m, d)
                    today = date.today()
                    if dob >= today:
                        message = 'Fecha de nacimiento inválida: no puede ser hoy ni en el futuro.'
                except Exception:
                    message = 'Formato de fecha inválido.'

                # Validaciones adicionales de edad según rol
                if not message:
                    try:
                        y, m, d = map(int, fecha_nac.split('-'))
                        dob = date(y, m, d)
                        today = date.today()
                        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                        if tipo_persona == 'representante' or tipo_persona == 'profesor':
                            if age < 18:
                                message = 'La persona debe ser mayor de 18 años para el rol seleccionado.'
                        elif tipo_persona == 'estudiante':
                            if age < 3 or age > 18:
                                message = 'Estudiante debe tener entre 3 y 18 años de edad.'
                    except Exception:
                        if not message:
                            message = 'Error al calcular la edad.'

            # si hay error, mostramos sin tocar BD
            if message:
                pass
            else:
                # comprobar duplicados no solo en personas sino también en persona_cedula
                try:
                    existing = None
                    if numero_cedula:
                        existing = db.session.execute(text(
                            'SELECT id_persona FROM personas WHERE numero_cedula = :num'
                        ), {'num': numero_cedula}).fetchone()
                        if not existing:
                            existing = db.session.execute(text(
                                'SELECT pc.id_persona FROM persona_cedula pc WHERE pc.numero_cedula = :num'
                            ), {'num': numero_cedula}).fetchone()
                except Exception:
                    existing = None

                if existing:
                    message = 'Persona ya registrada. No puedes volver a registrarla.'
                else:
                    try:
                        insert_person = text(
                            'INSERT INTO personas '
                            '(primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, fecha_nacimiento, id_sexo, id_tipo_persona, id_tipo_documento, numero_cedula, id_ocupacion, id_profesion, num_hijos, id_relacion_familiar) '
                            'VALUES (:primer, :segundo, :pap, :sap, :fecha, :id_sexo, :id_tipo_persona, :id_tipo_doc, :num_ced, :id_ocupacion, :id_profesion, :num_hijos, :id_relacion_familiar)'
                        )
                        db.session.execute(insert_person, {
                            'primer': primer,
                            'segundo': segundo or None,
                            'pap': pap,
                            'sap': sap or None,
                            'fecha': fecha_nac or None,
                            'id_sexo': id_sexo,
                            'id_tipo_persona': id_tipo_persona,
                            'id_tipo_doc': int(id_tipo_doc) if id_tipo_doc and str(id_tipo_doc).isdigit() else None,
                            'num_ced': numero_cedula or None,
                            'id_ocupacion': id_ocupacion,
                            'id_profesion': id_profesion,
                            'num_hijos': num_hijos,
                            'id_relacion_familiar': id_relacion_familiar
                        })
                        db.session.commit()

                        if db.engine.name == 'sqlite':
                            new_id = int(db.session.execute(text('SELECT last_insert_rowid()')).scalar() or 0)
                        else:
                            r = db.session.execute(text('SELECT LAST_INSERT_ID() as id')).fetchone()
                            new_id = int(r[0]) if r else 0

                        return redirect(url_for('registro_persona_ext', pid=new_id, tipo=id_tipo_persona))
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
            nombre = (f.get('nombre_plantel_nomina') or '').strip()
            codigo_pa = (f.get('codigo_pa') or '').strip()
            # validaciones iniciales
            if not nombre or not codigo_pa:
                message = 'Debe indicar nombre y código del plantel.'
            elif not codigo_pa.isdigit():
                message = 'El código PA debe contener solo dígitos.'
            elif len(codigo_pa) > 20:
                message = 'El código PA no puede exceder 20 caracteres.'
            else:
                try:
                    db.session.execute(
                        text('INSERT INTO planteles (codigo_pa, nombre_plantel_nomina) '
                             'VALUES (:codigo_pa, :nombre)')
                        , {'codigo_pa': codigo_pa, 'nombre': nombre}
                    )
                    db.session.commit()
                    message = 'Plantel registrado correctamente'
                except Exception as e:
                    db.session.rollback()
                    message = f'Error al registrar plantel: {e}'

        # ya no necesitamos cargar niveles ni cargos
        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'],
                               role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'),
                               roles_count=roles_count, users_by_role=users_by_role,
                               content_template='home_panel/registro_plantel.html', message=message)

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
