from flask import render_template, redirect, url_for, request, session, abort
from database.models import db
from sqlalchemy import text
from datetime import date

def tipo_de_registro_persona(tipo, ctx, roles_count, users_by_role):
    """Manejador de registros unificado."""
    allowed = [
        'plantel', 'personas', 'materias', 'secciones',
        'letra_seccion', 'grados', 'niveles', 'matriculas', 'personal_admin'
    ]
    if tipo not in allowed:
        return abort(404, 'Tipo de registro no válido')

    message = None

    def _cap_first(s):
        s = (s or '').strip()
        if not s:
            return ''
        return s[0].upper() + s[1:].lower()

    if tipo == 'personas':
        if request.method == 'POST':
            f = request.form
            try:
                # 1. Extracción y Normalización
                primer = _cap_first(f.get('primer_nombre'))
                segundo = _cap_first(f.get('segundo_nombre'))
                pap = _cap_first(f.get('primer_apellido'))
                sap = _cap_first(f.get('segundo_apellido'))
                fecha_nac = (f.get('fecha_nacimiento') or '').strip()
                numero_cedula = (f.get('numero_cedula') or '').strip()
                
                # 2. Manejo de IDs y Roles
                id_tipo_persona = int(f.get('id_tipo_persona') or 0)
                roles_map = {1: 'estudiante', 2: 'profesor', 3: 'representante', 4: 'empleado'}
                tipo_persona = roles_map.get(id_tipo_persona, '')

                # 3. Conversión de Género
                raw_sexo = f.get('id_sexo')
                id_sexo = int(raw_sexo) if raw_sexo and raw_sexo.isdigit() else None
                
                # 4. Datos adicionales
                id_tipo_doc = int(f.get('id_tipo_documento') or 1)
                num_hijos = int(f.get('num_hijos') or 0)
                
                def get_int_or_none(key):
                    val = f.get(key)
                    return int(val) if val and val.isdigit() else None

                id_ocupacion = get_int_or_none('id_ocupacion')
                id_profesion = get_int_or_none('id_profesion')
                id_relacion = get_int_or_none('id_relacion_familiar')

                # 5. Validaciones de Negocio
                if not numero_cedula or not primer or not pap or not fecha_nac or not tipo_persona:
                    message = 'Faltan campos obligatorios. Revise Cédula, Nombre, Apellido y Fecha.'
                else:
                    # Validación de Edad
                    birth_date = date.fromisoformat(fecha_nac)
                    today = date.today()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    
                    if tipo_persona == 'estudiante' and age > 18:
                        message = 'El estudiante no puede ser mayor de 18 años.'
                    elif tipo_persona in ['profesor', 'empleado', 'representante'] and age < 18:
                        message = 'El personal o representante debe ser mayor de edad.'
                    else:
                        # 6. Inserción SQL
                        query = text('''
                            INSERT INTO personas (
                                primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
                                numero_cedula, fecha_nacimiento, id_tipo_persona, id_sexo,
                                id_tipo_documento, num_hijos, id_ocupacion, id_profesion, id_relacion_familiar
                            ) VALUES (
                                :primer, :segundo, :pap, :sap, :cedula, :fecha, :tipo, :sexo, 
                                :doc, :hijos, :ocup, :prof, :rel
                            )
                        ''')
                        
                        result = db.session.execute(query, {
                            'primer': primer, 'segundo': segundo, 'pap': pap, 'sap': sap,
                            'cedula': numero_cedula, 'fecha': fecha_nac, 'tipo': id_tipo_persona,
                            'sexo': id_sexo, 'doc': id_tipo_doc, 'hijos': num_hijos,
                            'ocup': id_ocupacion, 'prof': id_profesion, 'rel': id_relacion
                        })
                        
                        new_id = result.lastrowid
                        db.session.commit()
                        
                        return redirect(url_for('registro_persona_ext', pid=new_id, tipo=tipo_persona))

            except Exception as e:
                db.session.rollback()
                print(f"DEBUG ERROR: {e}")
                message = f'Error en el sistema: {str(e)}'

        return render_template(
            'home_panel/struct.html',
            usuario=ctx['user'],
            developer_priv=ctx['developer_priv'],
            role_name=ctx.get('role_name'),
            role_desc=ctx.get('role_desc'),
            status=ctx.get('status'),
            roles_count=roles_count,
            users_by_role=users_by_role,
            content_template='home_panel/registro_persona_v2.html',
            message=message
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
