from flask import Flask, session, render_template, redirect, url_for, request
from dotenv import load_dotenv
import os

# Cargar .env
load_dotenv()

# Importar SQLAlchemy y blueprint
from database.models import db, Usuarios, Roles, StatusUser
from utiled.start import login_bp

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "162618")  # Usar variable de entorno para secret_key

# Obtener datos del archivo .env
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")

# Config SQLAlchemy: si faltan variables de entorno, usar SQLite por defecto (desarrollo)
if DB_USER and DB_PASS and DB_NAME and DB_HOST:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
else:
    sqlite_path = os.path.join(os.path.dirname(__file__), 'sidegeduc.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{sqlite_path}"
    print('DB: faltan credenciales MySQL. Usando SQLite de respaldo en', sqlite_path)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar BD
db.init_app(app)

# Crear tablas si es necesario (solo en entorno de desarrollo) para evitar errores al iniciar la app
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error creando tablas: {e}")

# Registrar blueprint de autenticación (login/register)
app.register_blueprint(login_bp)

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
    app.run(debug=True)