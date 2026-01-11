from flask import Flask
from dotenv import load_dotenv
import os

# Cargar .env
load_dotenv()

# Importar SQLAlchemy y blueprint
from database.models import db
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

# Registrar Blueprints
app.register_blueprint(login_bp)

if __name__ == "__main__":
    app.run(debug=True)