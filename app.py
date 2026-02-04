from flask import Flask, session, redirect, url_for, render_template
from dotenv import load_dotenv
import os
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Cargar variables de entorno
load_dotenv()

# --- IMPORTACIÓN DE MODELOS ---
# Importamos desde la ruta que SQLAlchemy reconozca según tu estructura
from database.models import db, Usuarios, Roles, StatusUser

from utiled.start import login_bp
# ---Importamos el mansejador de los permisos
from utiled.permissions import get_user_context

app = Flask(__name__)
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
        print("--- Tablas verificadas/creadas correctamente ---")
    except Exception as e:
        print(f"Aviso: No se pudieron crear tablas automáticamente: {e}")

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
import utiled.view_handlers as manejar_la_vista_de

# --- RUTAS ---

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
    return manejar_la_vista_de.constancia() 
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