
from flask import Flask, session, redirect, url_for, render_template, jsonify, request
from dotenv import load_dotenv
import os
import sys
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

# Cargar variables de entorno .env
load_dotenv()

# --- IMPORTACIÓN DE MODELOS ---
from database.models import db, Usuarios, Roles, StatusUser, TipoPersona, RelacionFamiliar, Ocupacion, Profesion
from utils.start import login_bp
from utils.permissions import get_user_context

# Detectar si se está ejecutando desde un ejecutable PyInstaller esto es para evitar error al compilar
if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
else:
    template_folder = 'templates'
    static_folder = 'static'

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
app.secret_key = os.getenv("SECRET_KEY", "162618")

# --- ENDPOINTS OCUPACIONES Y PROFESIONES (OPTIMIZADOS) ---
@app.route('/api/tipo_persona', methods=['GET'])
def get_tipo_persona():
    try:
        tipos = TipoPersona.query.all()
        return jsonify([{'id': t.id_tipo_persona, 'nombre': t.nombre_tipo_persona} for t in tipos])
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error al obtener tipos de persona: {str(e)}'}), 500
def _require_login_json():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'No autorizado. Inicie sesión.'}), 401
    return None

@app.route('/api/ocupaciones', methods=['GET'])
def get_ocupaciones():
    err = _require_login_json()
    if err:
        return err
    try:
        ocupaciones = Ocupacion.query.all()
        return jsonify([{'id': o.id, 'nombre': o.nombre} for o in ocupaciones])
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error al obtener ocupaciones: {str(e)}'}), 500

@app.route('/api/ocupaciones', methods=['POST'])
def add_ocupacion():
    err = _require_login_json()
    if err:
        return err
    nombre = request.json.get('nombre', '').strip()
    if not nombre:
        return jsonify({'success': False, 'error': 'Nombre requerido.'})
    try:
        nueva = Ocupacion(nombre=nombre)
        db.session.add(nueva)
        db.session.commit()
        return jsonify({'success': True})
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Ya existe.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Error inesperado: {str(e)}'})

@app.route('/api/profesiones', methods=['GET'])
def get_profesiones():
    err = _require_login_json()
    if err:
        return err
    try:
        profesiones = Profesion.query.all()
        return jsonify([{'id': p.id, 'nombre': p.nombre} for p in profesiones])
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error al obtener profesiones: {str(e)}'}), 500

@app.route('/api/profesiones', methods=['POST'])
def add_profesion():
    err = _require_login_json()
    if err:
        return err
    nombre = request.json.get('nombre', '').strip()
    if not nombre:
        return jsonify({'success': False, 'error': 'Nombre requerido.'})
    try:
        nueva = Profesion(nombre=nombre)
        db.session.add(nueva)
        db.session.commit()
        return jsonify({'success': True})
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Ya existe.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Error inesperado: {str(e)}'})

# --- CONFIGURACIÓN DE BASE DE DATOS (FORZAR SQLITE) ---
basedir = os.path.abspath(os.path.dirname(__file__))
sqlite_path = os.path.join(basedir, 'sidegeduc.db')

# Forzamos SQLite para evitar el error de "Access Denied" de MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{sqlite_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"--- DB: Sistema configurado para usar SQLite en: {sqlite_path} ---")

# --- ACTIVAR CLAVES FORÁNEAS EN SQLITE ---
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Inicializar SQLAlchemy
db.init_app(app)

# Crear tablas si no existen
with app.app_context():
    try:
        db.create_all()
        # en sqlite create_all no define algunas tablas si no hay un modelo
        # aseguramos manualmente la tabla planteles con columnas mínimas si aún no existe
        if app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite"):
            conn = db.engine.connect()
            existing = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='planteles';")).fetchone()
            if not existing:
                try:
                    conn.execute(text(
                        "CREATE TABLE planteles ("
                        "id_plantel INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "codigo_pa TEXT UNIQUE,"
                        "nombre_plantel_nomina TEXT"
                        ")"
                    ))
                    print("tabla 'planteles' creada manualmente")
                except Exception as ex:
                    print(f"Error creando tabla planteles: {ex}")

            # Algunos esquemas antiguos referencian una tabla niveles_academicos_escolares
            # (usada como FK desde la tabla representantes). Si el DB no la tiene, crearla
            # como alias de niveles_academicos para evitar errores de integridad.
            existing_niv = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='niveles_academicos_escolares';")).fetchone()
            if not existing_niv:
                try:
                    conn.execute(text(
                        "CREATE TABLE niveles_academicos_escolares ("
                        "id_nivel_academico INTEGER PRIMARY KEY,"
                        "nombre_nivel_academico VARCHAR(100) NOT NULL UNIQUE"
                        ")"
                    ))
                    conn.execute(text(
                        "INSERT OR IGNORE INTO niveles_academicos_escolares (id_nivel_academico, nombre_nivel_academico) "
                        "SELECT id_nivel_academico, nombre_nivel_academico FROM niveles_academicos"
                    ))
                    print("tabla 'niveles_academicos_escolares' creada y poblada (compatibilidad)")
                except Exception as ex:
                    print(f"Error creando tabla niveles_academicos_escolares: {ex}")

            conn.close()

            # Si la base de datos está vacía en los catálogos básicos, sembramos valores iniciales
            try:
                conn = db.engine.connect()
                # Niveles
                count = conn.execute(text('SELECT COUNT(1) FROM niveles')).scalar() or 0
                if count == 0:
                    for idx, nombre in enumerate(['Preescolar', 'Primaria', 'Secundaria'], start=1):
                        conn.execute(text('INSERT OR IGNORE INTO niveles (id_nivel, nombre_nivel) VALUES (:id, :nombre)'), {'id': idx, 'nombre': nombre})
                    print('Semilla: niveles insertados')

                # Grados
                count = conn.execute(text('SELECT COUNT(1) FROM grados')).scalar() or 0
                if count == 0:
                    for num in range(1, 7):
                        conn.execute(text('INSERT OR IGNORE INTO grados (id_grado, numero_grado) VALUES (:id, :numero)'), {'id': num, 'numero': num})
                    print('Semilla: grados insertados')

                # Letras de sección
                count = conn.execute(text('SELECT COUNT(1) FROM letra_seccion')).scalar() or 0
                if count == 0:
                    for idx, letra in enumerate(['A', 'B', 'C', 'D'], start=1):
                        conn.execute(text('INSERT OR IGNORE INTO letra_seccion (id_letra_seccion, letra) VALUES (:id, :letra)'), {'id': idx, 'letra': letra})
                    print('Semilla: letras de sección insertadas')

                # Asegurar que existan las tablas necesarias para asignar materias a secciones
                existing_materias = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='materias';")).fetchone()
                if not existing_materias:
                    conn.execute(text(
                        "CREATE TABLE materias ("
                        "id_materia INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "nombre_materia TEXT NOT NULL UNIQUE"
                        ")"
                    ))
                    print("tabla 'materias' creada (vacía)")

                # Asegurar que existan algunas materias de referencia
                for nombre in ['Matemáticas', 'Lengua y Literatura', 'Ciencias Sociales', 'Ciencias Naturales', 'Inglés']:
                    conn.execute(text('INSERT OR IGNORE INTO materias (nombre_materia) VALUES (:nombre)'), {'nombre': nombre})
                print('Semilla: materias básicas aseguradas (no se duplican)')

                existing_ms = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='materias_seccion';")).fetchone()
                if not existing_ms:
                    conn.execute(text(
                        "CREATE TABLE materias_seccion ("
                        "id_materia_nivel INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "id_materia INTEGER,"
                        "id_seccion INTEGER,"
                        "FOREIGN KEY(id_materia) REFERENCES materias(id_materia),"
                        "FOREIGN KEY(id_seccion) REFERENCES secciones(id_seccion)"
                        ")"
                    ))
                    print("tabla 'materias_seccion' creada (vacía)")

                conn.close()
            except Exception as ex:
                print(f'No se pudieron sembrar datos iniciales de secciones: {ex}')

        print("--- Tablas verificadas/creadas correctamente ---")
    except Exception as e:
        print(f"Aviso: No se pudieron crear tablas automáticamente: {e}")

    # Asegurar columnas adicionales en SQLite para compatibilidad con el esquema MySQL
    try: 
        if app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite"):
            conn = db.engine.connect()
            res = conn.execute(text("PRAGMA table_info(personas)")).fetchall()
            existing = [r[1] for r in res]
            needed = {
                'tipo_persona': 'TEXT',
                'id_tipo_documento': 'INTEGER',
                'numero_cedula': 'TEXT'
            }
            for col, ctype in needed.items():
                if col not in existing:
                    try:
                        conn.execute(text(f'ALTER TABLE personas ADD COLUMN {col} {ctype}'))
                        print(f'Columna {col} agregada a personas')
                    except Exception as ex:
                        print(f'No se pudo agregar columna {col}: {ex}')
            conn.close()
    except Exception as e:
        print(f'No se pudo asegurar columnas en SQLite: {e}')

# Registrar blueprint de autenticación
app.register_blueprint(login_bp)


@app.context_processor
def inject_user_context():
    
    try:
        ctx = get_user_context(session)
    except Exception:
        ctx = {}
    return {
        'is_creator': ctx.get('is_creator', False),
        'developer_priv': ctx.get('developer_priv', False),
        'role_name': ctx.get('role_name'),
        'role_desc': ctx.get('role_desc'),
        'status': ctx.get('status'),
        'usuario': ctx.get('user')
    }


# --- IMPORTACIÓN DE MANEJADORES DE VISTA ---
import utils.view_handlers as manejar_la_vista_de

# APIs auxiliares para operaciones específicas, como creación de ocupaciones o búsqueda de personas por cédula
@app.route('/api/ocupacion', methods=['POST'])
def api_ocupacion():
    return manejar_la_vista_de.api_create_ocupacion()

# API para detectar si una persona ya existe por su cédula
@app.route('/api/persona/lookup', methods=['GET'])
def api_persona_lookup():
    err = _require_login_json()
    if err:
        return err
    result = manejar_la_vista_de.api_lookup_persona_by_cedula()
    return jsonify(result) if isinstance(result, dict) else result

#api para crear una profesión si no existe, esto es para evitar que el usuario tenga que crear la profesión cada vez que registra a una persona nueva
@app.route('/api/profesion', methods=['POST'])
def api_profesion():
    return manejar_la_vista_de.api_create_profesion()

@app.route('/api/relaciones_familiares')
def get_relaciones_familiares():
    err = _require_login_json()
    if err:
        return err
    relaciones = RelacionFamiliar.query.all()
    return jsonify([{'id': r.id, 'nombre': r.nombre} for r in relaciones])


# --- RUTAS ---

# Registro de personas tipo wizard (paso a paso)
from flask import request, flash


@app.route('/registro_wizard', methods=['GET', 'POST'])
def registro_wizard_tipo():
    if request.method == 'POST':
        tipo_persona = request.form.get('tipo_persona')
        if tipo_persona:
            session['wizard_tipo_persona'] = tipo_persona
            return redirect(url_for('registro_wizard_datos'))
        else:
            flash('Selecciona un tipo de persona')
    tipos_persona = TipoPersona.query.all()
    return render_template('home_panel/registro_wizard_tipo.html', tipos_persona=tipos_persona)

@app.route('/registro_wizard/datos', methods=['GET', 'POST'])
def registro_wizard_datos():
    if request.method == 'POST':
        # Guardar datos personales en sesión
        session['wizard_primer_nombre'] = request.form.get('nombre1')
        session['wizard_segundo_nombre'] = request.form.get('nombre2')
        session['wizard_primer_apellido'] = request.form.get('apellido1')
        session['wizard_segundo_apellido'] = request.form.get('apellido2')
        session['wizard_fecha_nacimiento'] = request.form.get('fecha_nacimiento')
        session['wizard_tipo_cedula'] = request.form.get('tipo_cedula')
        # Validar aquí si es necesario
        return redirect(url_for('registro_wizard_familia'))
    # Pass the type of person name (not id) to the template so client-side scripts can read it
    tipo_nombre = ''
    tipo_id = session.get('wizard_tipo_persona')
    if tipo_id:
        try:
            tipo_obj = TipoPersona.query.get(int(tipo_id))
            if tipo_obj:
                # SQLAlchemy attribute name may vary
                tipo_nombre = getattr(tipo_obj, 'nombre_tipo_persona', '') or getattr(tipo_obj, 'nombre', '')
        except Exception:
            tipo_nombre = ''
    return render_template('home_panel/registro_wizard_datos.html',
                           wizard_tipo_persona=tipo_nombre)

@app.route('/registro_wizard/familia', methods=['GET', 'POST'])
def registro_wizard_familia():
    error_msg = None
    # Cargar relaciones familiares (para el select)
    try:
        import sqlite3
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id_parentesco, nombre_parentesco FROM parentescos")
        relaciones = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"Error consultando parentescos: {e}")
        relaciones = []

    if request.method == 'POST':
        cedula = (request.form.get('cedula') or '').strip()
        # Validar duplicado de cédula en la base de datos
        if cedula:
            try:
                exists = db.session.execute(text('SELECT 1 FROM personas WHERE numero_cedula = :cedula'), {'cedula': cedula}).fetchone()
                if exists:
                    error_msg = 'Error: Se a detectado que esta cedula ya la posee otra persona'
                else:
                    session['wizard_cedula'] = cedula
                    session['wizard_num_hijos'] = request.form.get('num_hijos')
                    session['wizard_relacion'] = request.form.get('relacion')
                    flash('Registro completado exitosamente')
                    return redirect(url_for('dashboard'))
            except Exception as e:
                print(f"Error validando cédula existente: {e}")
        else:
            error_msg = 'Debe ingresar una cédula válida.'

    return render_template('home_panel/registro_wizard_familia.html', relaciones=relaciones, error_msg=error_msg)

# API para obtener parentescos en formato JSON
@app.route('/api/parentescos', methods=['GET'])
def api_parentescos():
    from database.models import Parentesco
    try:
        parentescos = Parentesco.query.all()
        if not parentescos:
            return jsonify([])
        return jsonify([
            {
                'id_parentesco': p.id_parentesco,
                'nombre_parentesco': p.nombre_parentesco
            } for p in parentescos
        ])
    except Exception as e:
        print(f'Error consultando parentescos: {e}')
        return jsonify([])


# -- MANEJO DEL RESTO DE LAS RUTAS ---
@app.route('/dashboard')
def dashboard():
    return manejar_la_vista_de.home_panel()

@app.route('/')
def index():
    return manejar_la_vista_de.login()

@app.route('/boleta')
def boleta():
    return manejar_la_vista_de.boleta()

@app.route('/constancia')
def constancia():
    # Mantener ruta antigua, redirige/usa la nueva vista de consultas
    return manejar_la_vista_de.constancia()


@app.route('/consultas')
def consultas():
    return manejar_la_vista_de.consultas()


@app.route('/consultas/personas')
def consultas_personas():
    return manejar_la_vista_de.consultas_personas()


@app.route('/consultas/personas/list')
def consultas_personas_list():
    return manejar_la_vista_de.consultas_personas_list()


@app.route('/consultas/materias')
def consultas_materias():
    return manejar_la_vista_de.consultas_materias()


@app.route('/consultas/materias/editar', methods=['GET', 'POST'])
def consultas_materias_editar():
    return manejar_la_vista_de.consultas_materias_editar()


@app.route('/consultas/materias/borrar', methods=['POST'])
def consultas_materias_borrar():
    return manejar_la_vista_de.consultas_materias_borrar()


@app.route('/consultas/secciones')
def consultas_secciones():
    return manejar_la_vista_de.consultas_secciones()


@app.route('/consultas/planteles')
def consultas_planteles():
    return manejar_la_vista_de.consultas_planteles()


@app.route('/consultas/planteles/editar', methods=['GET', 'POST'])
def consultas_planteles_editar():
    return manejar_la_vista_de.consultas_planteles_editar()


@app.route('/consultas/planteles/borrar', methods=['POST'])
def consultas_planteles_borrar():
    return manejar_la_vista_de.consultas_planteles_borrar()


@app.route('/consultas/reporte/pdf/personas')
def reporte_pdf_personas():
    return manejar_la_vista_de.reporte_pdf_personas()


@app.route('/consultas/reporte/pdf/planteles')
def reporte_pdf_planteles():
    return manejar_la_vista_de.reporte_pdf_planteles()


@app.route('/consultas/reporte/pdf/secciones')
def reporte_pdf_secciones():
    return manejar_la_vista_de.reporte_pdf_secciones()


@app.route('/consultas/personas/list/editar')
def editar_registro_persona():
    return manejar_la_vista_de.editar_registro_persona()


@app.route('/consultas/personas/list/borrar', methods=['POST'])
def borrar_registro_persona():
    return manejar_la_vista_de.borrar_registro_persona()


@app.route('/consultas/personas/editar', methods=['GET', 'POST'])
def editar_persona():
    return manejar_la_vista_de.editar_persona()

@app.route('/admin_alumnos')
def admin_alumnos():
    return manejar_la_vista_de.admin_alumnos()

@app.route('/registros')
def registros_index():
    return manejar_la_vista_de.usuarios_roles_registrados()

@app.route('/registros/<tipo>', methods=['GET', 'POST'])
def registros_tipo(tipo):
    return manejar_la_vista_de.tipo_de_registro_persona(tipo)

@app.route('/developer/manage_user', methods=['GET', 'POST'])
def developer_manage_user():
    return manejar_la_vista_de.administrador_herramientas()


@app.route('/developer/secciones_existentes')
def developer_secciones_existentes():
    return manejar_la_vista_de.developer_secciones_existentes_vista()

@app.route('/developer/import_export', methods=['GET', 'POST'])
def developer_import_export():
    return manejar_la_vista_de.developer_import_export_vista()


@app.route('/user/configuracion', methods=['GET', 'POST'])
def user_configuracion():
    return manejar_la_vista_de.configuracion_de_usuario()
        

@app.route('/registros/persona/<int:pid>/<tipo>', methods=['GET', 'POST'])
def registro_persona_ext(pid, tipo):
    return manejar_la_vista_de.registro_persona_ext_vista(pid, tipo)

# Ruta de cierre de sesión
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login.login_handler'))

if __name__ == "__main__":
    # Importante: host='0.0.0.0' permite acceso en red local si fuera necesario
    app.run(debug=True)