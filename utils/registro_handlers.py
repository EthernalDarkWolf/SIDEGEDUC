from flask import render_template, redirect, url_for, request, session, abort, jsonify
from database.models import (
    db,
    Personas,
    Estudiantes,
    Profesores,
    Representantes,
    Empleados,
    Sexo,
    TipoDocumento,
    TipoPersona,
    Ocupacion,
    Profesion,
    Cargos,
    Grados,
    Niveles,
    LetraSeccion,
)
from sqlalchemy import text
from datetime import date
import unicodedata

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

    def _get_request_data():
        """Devuelve datos de la petición (form o JSON)."""
        if request.is_json:
            return request.get_json(silent=True) or {}
        return request.form

    def _api_response(success: bool, message: str, data: dict = None, status_code: int = 200):
        payload = {'success': success, 'message': message}
        if data is not None:
            payload['data'] = data
        return jsonify(payload), status_code

    def _normalize(value: str) -> str:
        """Normalize strings to compare ignoring accents/case/spacing."""
        if not value:
            return ''
        nfkd = unicodedata.normalize('NFKD', value)
        without_accents = ''.join(ch for ch in nfkd if unicodedata.category(ch) != 'Mn')
        return without_accents.strip().lower()

    if tipo == 'personas':
        if request.method == 'POST':
            f = _get_request_data()
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
                        # 6. Validación de duplicados (sin distinguir mayúsculas/acentos)
                        norm_name = _normalize(f"{primer} {pap}")
                        existing_cedula = db.session.execute(
                            text('SELECT 1 FROM personas WHERE numero_cedula = :cedula'),
                            {'cedula': numero_cedula}
                        ).fetchone()

                        if existing_cedula:
                            message = 'Error: Se a detectado que esta cedula ya la posee otra persona'
                        else:
                            # Comprobamos coincidencias por nombre+apellido+fecha de nacimiento
                            matches = db.session.execute(
                                text('SELECT primer_nombre, primer_apellido, fecha_nacimiento FROM personas WHERE fecha_nacimiento = :fecha'),
                                {'fecha': fecha_nac}
                            ).fetchall()
                            for r in matches:
                                if _normalize(f"{r['primer_nombre']} {r['primer_apellido']}") == norm_name:
                                    message = 'Ya existe una persona con esos datos.'
                                    break

                        if not message:
                            # 7. Inserción SQL
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

                            if tipo_persona == 'estudiante':
                                fecha_inscripcion = f.get('fecha_inscripcion')
                                db.session.execute(text('INSERT INTO estudiantes (id_persona, fecha_inscripcion) VALUES (:id, :fecins)'), { 'id': new_id, 'fecins': fecha_inscripcion  })

                            elif tipo_persona == 'representante':
                                db.session.execute(text('INSERT INTO representantes (id_persona, id_profesion, id_ocupacion) VALUES (:id, :id_profesion, :id_ocupacion)'), {
                                    'id': new_id,
                                    'id_profesion': id_profesion,
                                    'id_ocupacion': id_ocupacion
                                })
                            elif tipo_persona == 'profesor':
                                db.session.execute(text('INSERT INTO profesores (id_persona) VALUES (:id)'), { 'id': new_id })
                            elif tipo_persona == 'empleado':
                                otro_cargo = f.get('otro_cargo')
                                id_cargo = f.get('id_cargo')
                                salario = float(f.get('salario'))
                                fecha_contratacion = f.get('fecha_contratacion')
                                id_final_cargo = id_cargo

                                if id_cargo == 'otro':
                                    id_final_cargo = db.session.execute(text('INSERT INTO cargos (nombre_cargo) VALUES (:nombre_cargo)'), { 'nombre_cargo': otro_cargo}).lastrowid

                                db.session.execute(text('INSERT INTO empleados (id_persona, id_cargo, fecha_contratacion, salario) VALUES (:id_persona, :id_cargo, :fecha_contratacion, :salario)'), {
                                    'id_persona': new_id,
                                    'id_cargo': id_final_cargo,
                                    'fecha_contratacion': fecha_contratacion,
                                    'salario': salario,
                                })

                            db.session.commit()

                            success_msg = f"Registro del usuario \"{primer} {pap}\" completado"
                            if request.is_json:
                                return _api_response(True, success_msg, data={'id_persona': new_id})
                            return redirect(url_for('dashboard', message=success_msg))

            except Exception as e:
                db.session.rollback()
                print(f"DEBUG ERROR: {e}")
                message = f'Error en el sistema: {str(e)}'

            # Si la petición viene en JSON, devolvemos respuesta estructurada
            if request.is_json:
                return _api_response(False, message or 'Validación fallida')

        tipo_documentos = db.session.execute(text('SELECT id_tipo_documento, nombre_tipo_documento FROM tipo_documento')).fetchall()
        ocupaciones = db.session.execute(text('SELECT * FROM ocupaciones')).fetchall()
        cargos = db.session.execute(text('SELECT * FROM cargos')).fetchall()

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
            tipo_documentos=tipo_documentos,
            message=message,
            ocupaciones=ocupaciones,
            cargos=cargos,
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
            nombre_materia = (request.form.get('nombre_materia') or '').strip()
            if not nombre_materia:
                message = 'Debe indicar un nombre de materia.'
            else:
                # Validación de duplicados sin distinguir mayúsculas/acentos
                norm_new = _normalize(nombre_materia)
                existing = db.session.execute(text('SELECT nombre_materia FROM materias')).fetchall()
                for r in existing:
                    if _normalize(r['nombre_materia']) == norm_new:
                        message = 'Ya existe una materia con ese nombre.'
                        break

                if not message:
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
            data = _get_request_data()
            id_letra = data.get('id_letra_seccion') or data.get('id_letra')
            id_grado = data.get('id_grado')
            id_nivel = data.get('id_nivel')

            # Validaciones básicas
            if not id_letra or not id_grado or not id_nivel:
                message = 'Debe completar los campos: nivel, grado y letra.'
            else:
                try:
                    id_letra_i = int(id_letra)
                    id_grado_i = int(id_grado)
                    id_nivel_i = int(id_nivel)
                except Exception:
                    message = 'Valores inválidos para grado/nivel/letra.'
                else:
                    # Verificar que no exista ya
                    existing = db.session.execute(
                        text('SELECT 1 FROM secciones WHERE id_letra_seccion = :letra AND id_grado = :grado AND id_nivel = :nivel'),
                        {'letra': id_letra_i, 'grado': id_grado_i, 'nivel': id_nivel_i}
                    ).fetchone()
                    if existing:
                        message = 'La sección ya existe en el sistema.'
                    else:
                        try:
                            db.session.execute(
                                text('INSERT INTO secciones (id_letra_seccion, id_grado, id_nivel) VALUES (:id_letra, :id_grado, :id_nivel)'),
                                {'id_letra': id_letra_i, 'id_grado': id_grado_i, 'id_nivel': id_nivel_i}
                            )
                            db.session.commit()
                            message = 'Sección creada correctamente'
                            if request.is_json:
                                return _api_response(True, message, data={'id_letra_seccion': id_letra_i, 'id_grado': id_grado_i, 'id_nivel': id_nivel_i})
                        except Exception as e:
                            db.session.rollback()
                            message = f'Error al crear sección: {e}'
                            if request.is_json:
                                return _api_response(False, message)

            if request.is_json:
                return _api_response(False, message)

        # acciones: add_student, assign_professor, assign_materia
        if request.args.get('action') == 'add_student':
            if request.method == 'POST':
                f = _get_request_data()
                try:
                    db.session.execute(text('INSERT INTO estudiante_seccion (id_estudiante, id_seccion) VALUES (:est, :sec)'),
                                       {'est': f.get('id_estudiante'), 'sec': f.get('id_seccion')})
                    db.session.commit()
                    message = 'Estudiante asignado a sección correctamente'
                    if request.is_json:
                        return _api_response(True, message)
                except Exception as e:
                    db.session.rollback()
                    message = f'Error: {e}'
                    if request.is_json:
                        return _api_response(False, message)

        if request.args.get('action') == 'assign_professor':
            if request.method == 'POST':
                f = _get_request_data()
                try:
                    db.session.execute(text('INSERT INTO profesor_seccion (id_profesor, id_seccion) VALUES (:prof, :sec)'),
                                       {'prof': f.get('id_profesor'), 'sec': f.get('id_seccion')})
                    db.session.commit()
                    message = 'Profesor asignado a sección correctamente'
                    if request.is_json:
                        return _api_response(True, message)
                except Exception as e:
                    db.session.rollback()
                    message = f'Error: {e}'
                    if request.is_json:
                        return _api_response(False, message)

        if request.args.get('action') == 'assign_materia':
            if request.method == 'POST':
                f = _get_request_data()
                try:
                    db.session.execute(text('INSERT INTO materias_seccion (id_materia, id_seccion) VALUES (:mid, :sid)'),
                                       {'mid': f.get('id_materia'), 'sid': f.get('id_seccion')})
                    db.session.commit()
                    message = 'Materia asignada a sección correctamente'
                    if request.is_json:
                        return _api_response(True, message)
                except Exception as e:
                    db.session.rollback()
                    message = f'Error: {e}'
                    if request.is_json:
                        return _api_response(False, message)

        # cargar selects comunes
        estudiantes = db.session.execute(text('SELECT e.id_estudiante, p.primer_nombre, p.primer_apellido FROM estudiantes e JOIN personas p ON e.id_persona = p.id_persona')).fetchall()
        secciones_rows = db.session.execute(text('''
            SELECT s.id_seccion,
                   s.id_grado,
                   g.numero_grado,
                   s.id_nivel,
                   n.nombre_nivel,
                   s.id_letra_seccion,
                   l.letra
            FROM secciones s
            LEFT JOIN grados g ON g.id_grado = s.id_grado
            LEFT JOIN niveles n ON n.id_nivel = s.id_nivel
            LEFT JOIN letra_seccion l ON l.id_letra_seccion = s.id_letra_seccion
            ORDER BY n.nombre_nivel, g.numero_grado, l.letra
        ''')).mappings().all()  # devuelve lista de RowMapping

        # Convertir a diccionarios simples para que Jinja2 pueda serializar con tojson
        def _as_plain_dict(row):
            try:
                return dict(row)
            except Exception:
                try:
                    return dict(row._mapping)
                except Exception:
                    return {k: row[k] for k in row.keys()}

        secciones = [_as_plain_dict(r) for r in secciones_rows]
        profesores = db.session.execute(text('SELECT pr.id_profesor, p.primer_nombre, p.primer_apellido FROM profesores pr JOIN personas p ON pr.id_persona = p.id_persona')).fetchall()
        materias = db.session.execute(text('SELECT id_materia, nombre_materia FROM materias')).fetchall()
        letras = db.session.execute(text('SELECT id_letra_seccion, letra FROM letra_seccion ORDER BY letra')).fetchall()
        grados = db.session.execute(text('SELECT id_grado, numero_grado FROM grados ORDER BY numero_grado')).fetchall()
        niveles = db.session.execute(text('SELECT id_nivel, nombre_nivel FROM niveles ORDER BY nombre_nivel')).fetchall()

        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'],
                               role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'),
                               roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_secciones.html',
                               estudiantes=estudiantes, secciones=secciones, profesores=profesores, materias=materias,
                               letras=letras, grados=grados, niveles=niveles, message=message)

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
