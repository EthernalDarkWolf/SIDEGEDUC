
"""Módulo pequeño que expone el blueprint de autenticación.

Este archivo ahora sólo registra el blueprint `login_bp` y enlaza los
handlers que implementan la lógica de `login` y `register` en iniciar sesion.
"""
from flask import Blueprint
from sqlalchemy.exc import OperationalError

# Importar handlers que contienen la lógica real de las rutas
from .auth_handlers import login_handler, register_handler


login_bp = Blueprint('login', __name__)

# Registrar las rutas de autenticación en el blueprint
login_bp.add_url_rule('/login', view_func=login_handler, methods=['GET', 'POST'])
login_bp.add_url_rule('/register', view_func=register_handler, methods=['GET', 'POST'])

