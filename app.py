from flask import Flask, session, render_template, redirect, url_for, request
from dotenv import load_dotenv
import os

# Cargar .env
load_dotenv()

# Importar SQLAlchemy y blueprint
from database.models import db, Usuarios, Roles, StatusUser
from utiled.start import login_bp

app = Flask(__name__)
app.secret_key = "162618"  

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

# volver a Crear tablas si es necesario (solo en entorno de desarrollo) es para evitar errores al iniciar la app
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
    developer_priv = False
    if 'user_id' in session:
        uid = session.get('user_id')
        user_obj = Usuarios.query.filter_by(id_user=uid).first()
        if user_obj:
            user = user_obj.nombre
            role = Roles.query.filter_by(id_rol=user_obj.id_rol).first()
            role_name = (role.nombre_rol or '').lower() if role else ''
            # permitir privilegios si es desarrollador o personal administrativo
            if 'desarroll' in role_name or 'administr' in role_name or 'empleado' in role_name:
                developer_priv = True
    return render_template('home_panel/struct.html', usuario=user, developer_priv=developer_priv)


@app.route('/')
def index():
    if 'user_id' in session:
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


@app.route('/registros')
def registros_index():
    # Página índice de registros
    # mostrar dentro del layout principal
    # pasar usuario/privilegios similar a dashboard
    user = None
    developer_priv = False
    if 'user_id' in session:
        uid = session.get('user_id')
        user_obj = Usuarios.query.filter_by(id_user=uid).first()
        if user_obj:
            user = user_obj.nombre
            role = Roles.query.filter_by(id_rol=user_obj.id_rol).first()
            role_name = (role.nombre_rol or '').lower() if role else ''
            if 'desarroll' in role_name or 'administr' in role_name or 'empleado' in role_name:
                developer_priv = True
    return render_template('home_panel/struct.html', usuario=user, developer_priv=developer_priv, content_template='home_panel/registros.html')


@app.route('/registros/<tipo>', methods=['GET', 'POST'])
def registros_tipo(tipo):
    # tipos esperados: plantel, estudiantes, profesores, personal_admin, personal_obrero
    allowed = ['plantel', 'estudiantes', 'profesores', 'personal_admin', 'personal_obrero']
    if tipo not in allowed:
        return 'Tipo de registro no válido', 404
    title_map = {
        'plantel': 'Registro de Plantel',
        'estudiantes': 'Registro de Estudiantes',
        'profesores': 'Registro de Profesores',
        'personal_admin': 'Registro Personal Administrativo',
        'personal_obrero': 'Registro Personal Obrero'
    }
    # placeholder removed — use Flask's request if needed
    user = None
    developer_priv = False
    if 'user_id' in session:
        uid = session.get('user_id')
        user_obj = Usuarios.query.filter_by(id_user=uid).first()
        if user_obj:
            user = user_obj.nombre
            role = Roles.query.filter_by(id_rol=user_obj.id_rol).first()
            role_name = (role.nombre_rol or '').lower() if role else ''
            if 'desarroll' in role_name or 'administr' in role_name or 'empleado' in role_name:
                developer_priv = True
    return render_template('home_panel/struct.html', usuario=user, developer_priv=developer_priv, content_template='home_panel/registro_tipo.html', tipo=tipo, title=title_map.get(tipo, 'Registro'))


@app.route('/developer/manage_user', methods=['GET', 'POST'])
def developer_manage_user():
    # Sólo accesible para usuarios con rol desarrollador o personal administrativo
    if 'user_id' not in session:
        return redirect(url_for('login.login'))

    cur = Usuarios.query.filter_by(id_user=session.get('user_id')).first()
    if not cur:
        return redirect(url_for('login.login'))

    role = Roles.query.filter_by(id_rol=cur.id_rol).first()
    role_name = (role.nombre_rol or '').lower() if role else ''
    allowed = False
    if 'desarroll' in role_name or 'administr' in role_name or 'empleado' in role_name:
        allowed = True
    if not allowed:
        return 'Acceso denegado: privilegios insuficientes', 403

    # Excluir al usuario actual de la lista para evitar que se modifique a sí mismo
    users = Usuarios.query.filter(Usuarios.id_user != cur.id_user).order_by(Usuarios.nombre).all()
    roles = Roles.query.order_by(Roles.nombre_rol).all()
    statuses = StatusUser.query.order_by(StatusUser.estado).all()

    # obtener usuario actual y privilegios para render dentro del layout
    user = None
    developer_priv = True
    if 'user_id' in session:
        uo = Usuarios.query.filter_by(id_user=session.get('user_id')).first()
        if uo:
            user = uo.nombre
            current_user_id = uo.id_user

    if request.method == 'POST':
        form = request.form
        target = form.get('user_id')
        new_role = form.get('role_id')
        new_status = form.get('status_id')
        if target:
            target_user = Usuarios.query.filter_by(id_user=int(target)).first()
            if target_user:
                try:
                    if new_role:
                        target_user.id_rol = int(new_role)
                    if new_status:
                        target_user.id_status_user = int(new_status)
                    db.session.commit()
                    return render_template('home_panel/struct.html', usuario=user, developer_priv=developer_priv, content_template='home_panel/manage_user.html', users=users, roles=roles, statuses=statuses, message='Usuario actualizado correctamente', current_user_id=current_user_id if 'current_user_id' in locals() else None)
                except Exception as e:
                    db.session.rollback()
                    return render_template('home_panel/struct.html', usuario=user, developer_priv=developer_priv, content_template='home_panel/manage_user.html', users=users, roles=roles, statuses=statuses, message='Error al actualizar el usuario', current_user_id=current_user_id if 'current_user_id' in locals() else None)

    return render_template('home_panel/struct.html', usuario=user, developer_priv=developer_priv, content_template='home_panel/manage_user.html', users=users, roles=roles, statuses=statuses, current_user_id=current_user_id if 'current_user_id' in locals() else None)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login.login'))


if __name__ == "__main__":
    app.run(debug=True)