from flask import Flask, session, render_template, redirect, url_for
from dotenv import load_dotenv
import os

# Cargar .env
load_dotenv()

# Importar SQLAlchemy y blueprint
from database.models import db, Usuarios
from utiled.start import login_bp

app = Flask(__name__)
app.secret_key = "162618"  

# Obtener datos del .env
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")

# Config SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar BD
db.init_app(app)

# Crear tablas si es necesario (solo en entorno de desarrollo)
with app.app_context():
    try:
        db.create_all()
    except Exception:
        pass

# Registrar Blueprints
app.register_blueprint(login_bp)

@app.route('/dashboard')
def dashboard():
    user = None
    if 'username' in session:
        user = session.get('username')
    return render_template('home_panel/struct.html', usuario=user)


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login.login'))


@app.route('/boleta')
def boleta():
    return 'Boleta - en desarrollo'


@app.route('/constancia')
def constancia():
    return 'Constancia - en desarrollo'


@app.route('/admin_alumnos')
def admin_alumnos():
    return 'Administración de alumnos - en desarrollo'


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login.login'))


if __name__ == "__main__":
    app.run(debug=True)