from flask import Flask, session, redirect, url_for, render_template
from dotenv import load_dotenv
import os
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Cargar variables de entorno
load_dotenv()

# --- IMPORTACIÓN DE MODELOS ---
# Importamos desde la ruta que SQLAlchemy reconozca según tu estructura
try:
    from database.models import db, Usuarios, Roles, StatusUser
except ImportError:
    from models import db, Usuarios, Roles, StatusUser

from utiled.start import login_bp

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

# --- IMPORTACIÓN DE MANEJADORES DE VISTA ---
from utiled.view_handlers import (
    dashboard_view,
    index_view,
    boleta_view,
    constancia_view,
    admin_alumnos_view,
    registros_index_view,
    registros_tipo_view,
    developer_manage_user_view,
    developer_secciones_existentes_view,
    developer_import_export_view,
    registro_persona_ext_view,
)

# --- RUTAS ---

@app.route('/dashboard')
def dashboard():
    return dashboard_view()

@app.route('/')
def index():
    return index_view()

@app.route('/boleta')
def boleta():
    return boleta_view()

@app.route('/constancia')
def constancia():
    return constancia_view()

@app.route('/admin_alumnos')
def admin_alumnos():
    return admin_alumnos_view()

@app.route('/registros')
def registros_index():
    return registros_index_view()

@app.route('/registros/<tipo>', methods=['GET', 'POST'])
def registros_tipo(tipo):
    return registros_tipo_view(tipo)

@app.route('/developer/manage_user', methods=['GET', 'POST'])
def developer_manage_user():
    return developer_manage_user_view()

@app.route('/developer/secciones_existentes')
def developer_secciones_existentes():
    return developer_secciones_existentes_view()

@app.route('/developer/import_export', methods=['GET', 'POST'])
def developer_import_export():
    return developer_import_export_view()

@app.route('/registros/persona/<int:pid>/<tipo>', methods=['GET', 'POST'])
def registro_persona_ext(pid, tipo):
    return registro_persona_ext_view(pid, tipo)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login.login_handler'))

if __name__ == "__main__":
    # Importante: host='0.0.0.0' permite acceso en red local si fuera necesario
    app.run(debug=True)