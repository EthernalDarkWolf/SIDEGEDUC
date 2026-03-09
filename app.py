from flask import Flask, session, redirect, url_for, render_template
from dotenv import load_dotenv
import os
import sys
from sqlalchemy import event, text
from sqlalchemy.engine import Engine

# Cargar variables de entorno .env
load_dotenv()

# --- IMPORTACIÓN DE MODELOS ---
# Importamos desde la ruta que SQLAlchemy reconozca según tu estructura
from database.models import db, Usuarios, Roles, StatusUser, TipoPersona

from utils.start import login_bp

# ---Importamos el mansejador de los permisos
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
            conn.close()
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

#api para detectar si una persona ya existe por su cedula
@app.route('/api/persona/lookup', methods=['GET'])
def api_persona_lookup():
    return manejar_la_vista_de.api_lookup_persona_by_cedula()

#api para crear una profesión si no existe, esto es para evitar que el usuario tenga que crear la profesión cada vez que registra a una persona nueva
@app.route('/api/profesion', methods=['POST'])
def api_profesion():
    return manejar_la_vista_de.api_create_profesion()


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
    if request.method == 'POST':
        session['wizard_cedula'] = request.form.get('cedula')
        session['wizard_num_hijos'] = request.form.get('num_hijos')
        session['wizard_relacion'] = request.form.get('relacion')
        # Aquí puedes guardar todo en la BD o mostrar resumen
        # Limpiar sesión si es necesario
        flash('Registro completado exitosamente')
        return redirect(url_for('dashboard'))
    return render_template('home_panel/registro_wizard_familia.html')


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