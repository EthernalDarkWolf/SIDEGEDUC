import logging
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
from .change_history import log_change

logger = logging.getLogger(__name__)

def tipo_de_registro_persona(tipo, ctx, roles_count, users_by_role):
    """Manejador de registros unificado."""
    allowed = [
        'plantel', 'personas', 'materias', 'secciones',
        'letra_seccion', 'grados', 'niveles', 'matriculas', 'personal_admin'
    ]
    if tipo not in allowed:
        return abort(404, 'Tipo de registro no válido')

    message = None
    actor_id = session.get('user_id')
    actor_name = ctx.get('user') if isinstance(ctx, dict) else None

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
        def _ensure_estudiante_responsable_table():
            """Garantiza tabla de vínculo estudiante-responsable en SQLite."""
            try:
                db.session.execute(text('''
                    CREATE TABLE IF NOT EXISTS estudiante_responsable (
                        id_estudiante_responsable INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_estudiante INTEGER NOT NULL,
                        id_persona_responsable INTEGER NOT NULL,
                        numero_hijo INTEGER NOT NULL,
                        fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(id_persona_responsable, numero_hijo),
                        UNIQUE(id_estudiante),
                        FOREIGN KEY(id_estudiante) REFERENCES estudiantes(id_estudiante),
                        FOREIGN KEY(id_persona_responsable) REFERENCES personas(id_persona)
                    )
                '''))
                db.session.commit()
            except Exception:
                db.session.rollback()

        def _adultos_responsables_disponibles():
            """
            Devuelve adultos (profesor/representante/empleado) con cupo de hijos disponible.
            El cupo se calcula por num_hijos - hijos ya vinculados en estudiante_responsable.
            """
            _ensure_estudiante_responsable_table()
            rows = db.session.execute(text('''
                SELECT
                    p.id_persona,
                    p.primer_nombre,
                    p.primer_apellido,
                    p.numero_cedula,
                    tp.nombre_tipo_persona,
                    COALESCE(p.num_hijos, 0) AS total_hijos,
                    (
                        SELECT COUNT(*)
                        FROM estudiante_responsable er
                        WHERE er.id_persona_responsable = p.id_persona
                    ) AS hijos_vinculados
                FROM personas p
                JOIN tipo_persona tp ON tp.id_tipo_persona = p.id_tipo_persona
                WHERE p.id_tipo_persona IN (2, 3, 4)
                  AND COALESCE(p.num_hijos, 0) > 0
                ORDER BY p.primer_nombre, p.primer_apellido
            ''')).mappings().all()

            disponibles = []
            for r in rows:
                total_hijos = int(r.get('total_hijos') or 0)
                hijos_vinculados = int(r.get('hijos_vinculados') or 0)
                if total_hijos <= hijos_vinculados:
                    continue
                disponibles.append({
                    'id_persona': int(r.get('id_persona')),
                    'primer_nombre': (r.get('primer_nombre') or '').strip(),
                    'primer_apellido': (r.get('primer_apellido') or '').strip(),
                    'tipo_persona': (r.get('nombre_tipo_persona') or '').strip(),
                    'numero_cedula': (r.get('numero_cedula') or '').strip() if r.get('numero_cedula') is not None else '',
                    'total_hijos': total_hijos,
                    'hijos_vinculados': hijos_vinculados,
                    'hijos_disponibles': max(total_hijos - hijos_vinculados, 0),
                })
            return disponibles

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
                
                def safe_int(val, default=0):
                    if val is None or val == '':
                        return default
                    if isinstance(val, int):
                        return val
                    if isinstance(val, str):
                        s = val.strip()
                        if s.isdigit():
                            return int(s)
                        return default
                    return default

                # 2. Manejo de IDs y Roles
                id_tipo_persona = safe_int(f.get('id_tipo_persona'), 0)
                roles_map = {1: 'estudiante', 2: 'profesor', 3: 'representante', 4: 'empleado'}
                tipo_persona = roles_map.get(id_tipo_persona, '')

                # 3. Conversión de Género
                raw_sexo = f.get('id_sexo')
                id_sexo = safe_int(raw_sexo, None) if raw_sexo not in (None, '') else None
                
                # 4. Datos adicionales (id_tipo_documento puede venir como texto del frontend)
                raw_tipo_doc = f.get('id_tipo_documento')
                if raw_tipo_doc and isinstance(raw_tipo_doc, str) and not str(raw_tipo_doc).strip().isdigit():
                    tipo_docs = db.session.execute(text('SELECT id_tipo_documento, nombre_tipo_documento FROM tipo_documento')).fetchall()
                    busca = _normalize(str(raw_tipo_doc))
                    id_tipo_doc = 1
                    for td in tipo_docs:
                        try:
                            tid = int(td[0]) if td[0] is not None else 1
                            nom = _normalize(str(td[1] or ''))
                            if busca and nom and (busca == nom or busca in nom or nom in busca):
                                id_tipo_doc = tid
                                break
                        except (IndexError, TypeError, ValueError):
                            continue
                else:
                    id_tipo_doc = safe_int(raw_tipo_doc, 1)
                num_hijos = safe_int(f.get('num_hijos'), 0)
                
                def get_int_or_none(key):
                    val = f.get(key)
                    if val is None or val == '':
                        return None
                    if isinstance(val, int):
                        return val
                    if isinstance(val, str) and val.isdigit():
                        return int(val)
                    return None

                id_ocupacion = get_int_or_none('id_ocupacion')
                id_profesion = get_int_or_none('id_profesion')
                id_relacion = get_int_or_none('id_relacion_familiar')
                id_adulto_responsable = get_int_or_none('id_adulto_responsable')
                numero_hijo_responsable = get_int_or_none('numero_hijo_responsable')

                # 5. Validaciones de Negocio
                if not numero_cedula or not primer or not pap or not fecha_nac or not tipo_persona:
                    message = 'Faltan campos obligatorios. Revise Cédula, Nombre, Apellido y Fecha.'
                else:
                    # Validación de Edad
                    try:
                        birth_date = date.fromisoformat(fecha_nac)
                    except (ValueError, TypeError):
                        message = 'Fecha de nacimiento inválida. Use formato AAAA-MM-DD.'
                        birth_date = None
                    if birth_date:
                        today = date.today()
                        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                        if tipo_persona == 'estudiante' and (age < 3 or age > 13):
                            message = 'El estudiante debe tener entre 3 y 13 años.'
                        elif tipo_persona in ['profesor', 'empleado', 'representante'] and age < 18:
                            message = 'El personal o representante debe ser mayor de edad.'
                        if not message and tipo_persona == 'estudiante':
                            # Reglas especiales de estudiante:
                            # - no requiere ocupación/profesión/relación familiar
                            # - fecha de inscripción siempre es hoy
                            # - si es menor, tipo documento fijo "Cédula Escolar"
                            id_ocupacion = None
                            id_profesion = None
                            id_relacion = None
                            num_hijos = 0

                            if age < 18:
                                # Buscar tipo documento "Cédula Escolar" por nombre
                                tipo_docs = db.session.execute(
                                    text('SELECT id_tipo_documento, nombre_tipo_documento FROM tipo_documento')
                                ).fetchall()
                                id_cedula_escolar = None
                                for td in tipo_docs:
                                    try:
                                        tid = int(td[0]) if td[0] is not None else None
                                        nom = _normalize(str(td[1] or ''))
                                        if nom == _normalize('Cédula Escolar') or nom == _normalize('Cedula Escolar'):
                                            id_cedula_escolar = tid
                                            break
                                    except (IndexError, TypeError, ValueError):
                                        continue
                                if id_cedula_escolar is not None:
                                    id_tipo_doc = id_cedula_escolar

                                if not id_adulto_responsable or not numero_hijo_responsable:
                                    message = 'Para estudiante menor de edad debe seleccionar adulto responsable y número de hijo.'
                                elif numero_hijo_responsable < 1:
                                    message = 'El número de hijo debe ser mayor o igual a 1.'
                                else:
                                    adulto = db.session.execute(text('''
                                        SELECT id_persona, numero_cedula, COALESCE(num_hijos, 0) AS num_hijos
                                        FROM personas
                                        WHERE id_persona = :id
                                          AND id_tipo_persona IN (2, 3, 4)
                                    '''), {'id': id_adulto_responsable}).mappings().first()

                                    if not adulto:
                                        message = 'El adulto responsable seleccionado no es válido.'
                                    else:
                                        total_hijos_adulto = int(adulto.get('num_hijos') or 0)
                                        if total_hijos_adulto < 1:
                                            message = 'El adulto responsable no tiene hijos registrados.'
                                        elif numero_hijo_responsable > total_hijos_adulto:
                                            message = f'El adulto responsable solo tiene {total_hijos_adulto} hijo(s) registrados.'
                                        else:
                                            _ensure_estudiante_responsable_table()
                                            ocupacion_hijo = db.session.execute(text('''
                                                SELECT 1
                                                FROM estudiante_responsable
                                                WHERE id_persona_responsable = :id_adulto
                                                  AND numero_hijo = :num_hijo
                                                LIMIT 1
                                            '''), {
                                                'id_adulto': id_adulto_responsable,
                                                'num_hijo': numero_hijo_responsable
                                            }).fetchone()
                                            if ocupacion_hijo:
                                                message = 'Ese número de hijo ya está vinculado a otro estudiante para el adulto responsable seleccionado.'
                                            else:
                                                fecha_base = birth_date.strftime('%Y%m%d')
                                                ultimo_digito_adulto = ''.join(ch for ch in str(adulto.get('numero_cedula') or '') if ch.isdigit())
                                                ultimo_digito_adulto = (ultimo_digito_adulto[-1] if ultimo_digito_adulto else '0')
                                                numero_cedula = f'{fecha_base}{numero_hijo_responsable}{ultimo_digito_adulto}'
                    if not message:
                        # Reglas de hijos/relación por tipo de persona:
                        # - Representante: obligatorio >= 1 hijo y relación familiar.
                        # - Profesor/Empleado: permite 0 hijos; relación solo si tiene hijos.
                        if tipo_persona == 'representante':
                            if num_hijos < 1:
                                message = 'El representante debe tener al menos 1 hijo.'
                            elif not id_relacion:
                                message = 'Debe seleccionar la relación familiar del representante con el/los hijo(s).'
                        elif tipo_persona in ['profesor', 'empleado']:
                            if num_hijos <= 0:
                                num_hijos = 0
                                id_relacion = None
                            elif not id_relacion:
                                message = 'Debe seleccionar la relación familiar cuando tenga hijos registrados.'
                    if not message and tipo_persona in ['profesor', 'empleado'] and id_ocupacion:
                        # Regla de negocio: profesor/empleado no puede tener ocupación jubilado/a.
                        occ = db.session.execute(
                            text('SELECT nombre FROM ocupaciones WHERE id = :id LIMIT 1'),
                            {'id': id_ocupacion}
                        ).fetchone()
                        occ_nombre = _normalize(str(occ[0] if occ and occ[0] is not None else ''))
                        if occ_nombre in [_normalize('Jubilado/a'), _normalize('Jubilado'), _normalize('Jubilada')]:
                            message = 'La ocupación "Jubilado/a" no aplica para profesor o empleado.'
                    if not message:
                        # 6. Validación de duplicados (sin distinguir mayúsculas/acentos)
                        norm_name = _normalize(f"{primer} {pap}")
                        existing_cedula = db.session.execute(
                            text('SELECT 1 FROM personas WHERE numero_cedula = :cedula'),
                            {'cedula': numero_cedula}
                        ).fetchone()

                        if existing_cedula:
                            message = 'Error: Se ha detectado que esta cédula ya la posee otra persona.'
                        else:
                            # Comprobamos coincidencias por nombre+apellido+fecha de nacimiento
                            matches = db.session.execute(
                                text('SELECT primer_nombre, primer_apellido, fecha_nacimiento FROM personas WHERE fecha_nacimiento = :fecha'),
                                {'fecha': fecha_nac}
                            ).fetchall()
                            for r in matches:
                                pn = r[0] if len(r) > 0 else getattr(r, '_mapping', {}).get('primer_nombre', '') or ''
                                pa = r[1] if len(r) > 1 else getattr(r, '_mapping', {}).get('primer_apellido', '') or ''
                                if pn is None: pn = ''
                                if pa is None: pa = ''
                                if _normalize(f"{pn} {pa}") == norm_name:
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
                            
                            db.session.execute(query, {
                                'primer': primer, 'segundo': segundo, 'pap': pap, 'sap': sap,
                                'cedula': numero_cedula, 'fecha': fecha_nac, 'tipo': id_tipo_persona,
                                'sexo': id_sexo, 'doc': id_tipo_doc, 'hijos': num_hijos,
                                'ocup': id_ocupacion, 'prof': id_profesion, 'rel': id_relacion
                            })
                            row = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()
                            new_id = int(row[0]) if row and row[0] else None
                            if not new_id:
                                raise ValueError('No se pudo obtener el ID de la persona registrada.')

                            if tipo_persona == 'estudiante':
                                fecha_inscripcion = date.today().isoformat()
                                db.session.execute(text('INSERT INTO estudiantes (id_persona, fecha_inscripcion) VALUES (:id, :fecins)'), {'id': new_id, 'fecins': fecha_inscripcion})
                                if id_adulto_responsable and numero_hijo_responsable:
                                    _ensure_estudiante_responsable_table()
                                    id_estudiante_row = db.session.execute(
                                        text('SELECT id_estudiante FROM estudiantes WHERE id_persona = :id_persona LIMIT 1'),
                                        {'id_persona': new_id}
                                    ).fetchone()
                                    id_estudiante = int(id_estudiante_row[0]) if id_estudiante_row and id_estudiante_row[0] else None
                                    if id_estudiante:
                                        db.session.execute(text('''
                                            INSERT INTO estudiante_responsable (
                                                id_estudiante, id_persona_responsable, numero_hijo
                                            ) VALUES (:id_estudiante, :id_persona_responsable, :numero_hijo)
                                        '''), {
                                            'id_estudiante': id_estudiante,
                                            'id_persona_responsable': id_adulto_responsable,
                                            'numero_hijo': numero_hijo_responsable
                                        })

                            elif tipo_persona == 'representante':
                                db.session.execute(text('INSERT INTO representantes (id_persona, id_profesion, id_ocupacion) VALUES (:id, :id_profesion, :id_ocupacion)'), {
                                    'id': new_id,
                                    'id_profesion': id_profesion,
                                    'id_ocupacion': id_ocupacion
                                })
                            elif tipo_persona == 'profesor':
                                db.session.execute(text('INSERT INTO profesores (id_persona) VALUES (:id)'), { 'id': new_id })
                            elif tipo_persona == 'empleado':
                                otro_cargo = (f.get('otro_cargo') or '').strip()
                                id_cargo = f.get('id_cargo')
                                salario_val = f.get('salario')
                                try:
                                    salario = float(salario_val) if salario_val not in (None, '') else 0.0
                                except (ValueError, TypeError):
                                    salario = 0.0
                                fecha_contratacion = (f.get('fecha_contratacion') or '').strip() or None

                                if id_cargo == 'otro' and otro_cargo:
                                    res = db.session.execute(text('INSERT INTO cargos (nombre_cargo) VALUES (:nombre_cargo)'), {'nombre_cargo': otro_cargo})
                                    id_final_cargo = res.lastrowid if hasattr(res, 'lastrowid') and res.lastrowid else db.session.execute(text('SELECT last_insert_rowid()')).scalar()
                                else:
                                    id_final_cargo = get_int_or_none('id_cargo') if id_cargo != 'otro' else None

                                if id_final_cargo is not None:
                                    db.session.execute(text('INSERT INTO empleados (id_persona, id_cargo, fecha_contratacion, salario) VALUES (:id_persona, :id_cargo, :fecha_contratacion, :salario)'), {
                                        'id_persona': new_id,
                                        'id_cargo': id_final_cargo,
                                        'fecha_contratacion': fecha_contratacion,
                                        'salario': salario,
                                    })
                                else:
                                    raise ValueError('Debe seleccionar o especificar un cargo válido.')

                            db.session.commit()

                            success_msg = f"Registro del usuario \"{primer} {pap}\" completado"
                            if request.is_json:
                                return _api_response(True, success_msg, data={'id_persona': new_id})
                            return redirect(url_for('dashboard', message=success_msg))

            except Exception as e:
                db.session.rollback()
                logger.exception('Error al registrar persona')
                message = 'Error en el sistema. Verifique los datos e intente de nuevo.'

            # Si la petición viene en JSON, devolvemos respuesta estructurada
            if request.is_json:
                return _api_response(False, message or 'Validación fallida')

        tipo_documentos = db.session.execute(text('SELECT id_tipo_documento, nombre_tipo_documento FROM tipo_documento')).fetchall()
        ocupaciones = db.session.execute(text('SELECT * FROM ocupaciones')).fetchall()
        cargos = db.session.execute(text('SELECT * FROM cargos')).fetchall()
        responsables_disponibles = _adultos_responsables_disponibles()

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
            responsables_disponibles=responsables_disponibles,
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
                    res = db.session.execute(
                        text('INSERT INTO planteles (codigo_pa, nombre_plantel_nomina) '
                             'VALUES (:codigo_pa, :nombre)')
                        , {'codigo_pa': codigo_pa, 'nombre': nombre}
                    )
                    row = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()
                    new_id = int(row[0]) if row and row[0] else None
                    log_change(actor_id, actor_name, 'create', 'plantel', new_id,
                               f'Se agrego plantel: {nombre}',
                               payload={'id_plantel': new_id, 'nombre': nombre, 'codigo_pa': codigo_pa},
                               undo_supported=True)
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
                # Consulta para validar duplicados sin depender de la colación de la BD.
                normalized_new = _normalize(nombre_materia)
                exists = db.session.execute(text('SELECT nombre_materia FROM materias')).fetchall()
                duplicated = any(_normalize((row[0] or '')) == normalized_new for row in exists if row and row[0] is not None)
                if duplicated:
                    message = 'Ya existe una materia con ese nombre. No se permite el registro de materias duplicadas.'

                if not message:
                    try:
                        db.session.execute(text('INSERT INTO materias (nombre_materia) VALUES (:name)'), {'name': nombre_materia})
                        row = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()
                        new_id = int(row[0]) if row and row[0] else None
                        log_change(actor_id, actor_name, 'create', 'materia', new_id,
                                   f'Se agrego materia: {nombre_materia}',
                                   payload={'id_materia': new_id, 'nombre_materia': nombre_materia},
                                   undo_supported=True)
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

        def _ensure_assignment_tables():
            """Garantiza tablas puente para asignaciones en SQLite."""
            try:
                # Si existe, no hace nada; si no, la crea.
                db.session.execute(text('''
                    CREATE TABLE IF NOT EXISTS estudiante_seccion (
                        id_estudiante_seccion INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_estudiante INTEGER,
                        id_seccion INTEGER
                    )
                '''))
                db.session.execute(text('''
                    CREATE TABLE IF NOT EXISTS profesor_seccion (
                        id_profesor_seccion INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_profesor INTEGER,
                        id_seccion INTEGER
                    )
                '''))
                db.session.commit()
            except Exception:
                db.session.rollback()

        _ensure_assignment_tables()
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
                            row = db.session.execute(text('SELECT last_insert_rowid()')).fetchone()
                            new_id = int(row[0]) if row and row[0] else None
                            log_change(actor_id, actor_name, 'create', 'seccion', new_id,
                                       'Se creo una nueva seccion',
                                       payload={'id_seccion': new_id, 'id_letra_seccion': id_letra_i, 'id_grado': id_grado_i, 'id_nivel': id_nivel_i},
                                       undo_supported=True)
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
                    id_est = int(f.get('id_estudiante') or 0)
                    id_sec = int(f.get('id_seccion') or 0)
                    if not id_est or not id_sec:
                        raise ValueError('Debe seleccionar estudiante y sección.')

                    exists_student = db.session.execute(
                        text('SELECT 1 FROM estudiantes WHERE id_estudiante = :id'),
                        {'id': id_est}
                    ).fetchone()
                    exists_section = db.session.execute(
                        text('SELECT 1 FROM secciones WHERE id_seccion = :id'),
                        {'id': id_sec}
                    ).fetchone()
                    if not exists_student or not exists_section:
                        raise ValueError('Estudiante o sección no válida.')

                    already_linked = db.session.execute(
                        text('SELECT id_seccion FROM estudiante_seccion WHERE id_estudiante = :id'),
                        {'id': id_est}
                    ).fetchone()
                    if already_linked:
                        raise ValueError('Este estudiante ya está vinculado a una sección.')

                    row_count = db.session.execute(
                        text('SELECT COUNT(*) FROM estudiante_seccion WHERE id_seccion = :sec'),
                        {'sec': id_sec}
                    ).fetchone()
                    count_val = int(row_count[0]) if row_count and row_count[0] is not None else 0
                    if count_val >= 30:
                        raise ValueError('Esta sección ya alcanzó el cupo máximo de 30 estudiantes.')

                    db.session.execute(
                        text('INSERT INTO estudiante_seccion (id_estudiante, id_seccion) VALUES (:est, :sec)'),
                        {'est': id_est, 'sec': id_sec}
                    )
                    log_change(actor_id, actor_name, 'link', 'estudiante_seccion', None,
                               'Se asigno estudiante a seccion',
                               payload={'id_estudiante': id_est, 'id_seccion': id_sec},
                               undo_supported=True)
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
                    id_prof = int(f.get('id_profesor') or 0)
                    id_sec = int(f.get('id_seccion') or 0)
                    if not id_prof or not id_sec:
                        raise ValueError('Debe seleccionar profesor y sección.')

                    exists_prof = db.session.execute(
                        text('SELECT 1 FROM profesores WHERE id_profesor = :id'),
                        {'id': id_prof}
                    ).fetchone()
                    exists_section = db.session.execute(
                        text('SELECT 1 FROM secciones WHERE id_seccion = :id'),
                        {'id': id_sec}
                    ).fetchone()
                    if not exists_prof or not exists_section:
                        raise ValueError('Profesor o sección no válida.')

                    sec_has_prof = db.session.execute(
                        text('SELECT 1 FROM profesor_seccion WHERE id_seccion = :sec LIMIT 1'),
                        {'sec': id_sec}
                    ).fetchone()
                    if sec_has_prof:
                        raise ValueError('Esta sección ya tiene un profesor asignado.')

                    prof_already = db.session.execute(
                        text('SELECT 1 FROM profesor_seccion WHERE id_profesor = :prof LIMIT 1'),
                        {'prof': id_prof}
                    ).fetchone()
                    if prof_already:
                        raise ValueError('Este profesor ya está vinculado a otra sección.')

                    db.session.execute(
                        text('INSERT INTO profesor_seccion (id_profesor, id_seccion) VALUES (:prof, :sec)'),
                        {'prof': id_prof, 'sec': id_sec}
                    )
                    log_change(actor_id, actor_name, 'link', 'profesor_seccion', None,
                               'Se asigno profesor a seccion',
                               payload={'id_profesor': id_prof, 'id_seccion': id_sec},
                               undo_supported=True)
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
                    log_change(actor_id, actor_name, 'link', 'materia_seccion', None,
                               'Se asigno materia a seccion',
                               payload={'id_materia': f.get('id_materia'), 'id_seccion': f.get('id_seccion')},
                               undo_supported=True)
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

        # Disponibilidad para UX: estudiantes/profesores no vinculados y secciones con cupo.
        try:
            assigned_students_rows = db.session.execute(text('SELECT id_estudiante FROM estudiante_seccion')).fetchall()
        except Exception:
            assigned_students_rows = []
        assigned_students = {int(r[0]) for r in assigned_students_rows if r and r[0] is not None}
        estudiantes_disponibles = [e for e in estudiantes if int(e[0]) not in assigned_students]

        try:
            assigned_prof_rows = db.session.execute(text('SELECT id_profesor FROM profesor_seccion')).fetchall()
        except Exception:
            assigned_prof_rows = []
        assigned_profesores = {int(r[0]) for r in assigned_prof_rows if r and r[0] is not None}
        profesores_disponibles = [p for p in profesores if int(p[0]) not in assigned_profesores]

        try:
            section_student_count_rows = db.session.execute(
                text('SELECT id_seccion, COUNT(*) FROM estudiante_seccion GROUP BY id_seccion')
            ).fetchall()
        except Exception:
            section_student_count_rows = []
        student_count_by_section = {int(r[0]): int(r[1]) for r in section_student_count_rows if r and r[0] is not None}

        try:
            section_has_prof_rows = db.session.execute(text('SELECT DISTINCT id_seccion FROM profesor_seccion')).fetchall()
        except Exception:
            section_has_prof_rows = []
        section_has_prof = {int(r[0]) for r in section_has_prof_rows if r and r[0] is not None}

        secciones_para_estudiantes = [s for s in secciones if int(s.get('id_seccion') or 0) and student_count_by_section.get(int(s.get('id_seccion')), 0) < 30]
        secciones_para_profesores = [s for s in secciones if int(s.get('id_seccion') or 0) and int(s.get('id_seccion')) not in section_has_prof]

        return render_template('home_panel/struct.html', usuario=ctx['user'], developer_priv=ctx['developer_priv'],
                               role_name=ctx.get('role_name'), role_desc=ctx.get('role_desc'), status=ctx.get('status'),
                               roles_count=roles_count, users_by_role=users_by_role, content_template='home_panel/registro_secciones.html',
                               estudiantes=estudiantes, secciones=secciones, profesores=profesores, materias=materias,
                               letras=letras, grados=grados, niveles=niveles, message=message,
                               estudiantes_disponibles=estudiantes_disponibles, profesores_disponibles=profesores_disponibles,
                               secciones_para_estudiantes=secciones_para_estudiantes, secciones_para_profesores=secciones_para_profesores,
                               student_count_by_section=student_count_by_section)

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
