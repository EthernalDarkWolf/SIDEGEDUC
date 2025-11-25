from flask import render_template, request, render_template_string
from .database.Models.models import usuarios, roles, status_user
from .database.Models import db



# ==========================
# FUNCIONES DE BASE DE DATOS
# ==========================

def validar(usuario, clave):
    """Valida el usuario y contraseña desde la base de datos."""
    usuario_db = usuarios.query.filter_by(nombre=usuario).first()
    if usuario_db is None:
        return False


    # Aquí puedes agregar en el futuro hashing (bcrypt)
    return usuario_db.contrasena == clave


def registrar_usuario(usuario, clave):
    """Registra un usuario nuevo en la base de datos."""

    # Revisar si el usuario ya existe
    if usuarios.query.filter_by(nombre=usuario).first():
        return False

    # Buscar rol por defecto
    rol_default = roles.query.filter_by(nombre_rol="Estudiante").first()

    # Si no existe el rol, crearlo automáticamente
    if rol_default is None:
        rol_default = roles(nombre_rol="Estudiante")
        db.session.add(rol_default)
        db.session.commit()

    # Crear usuario nuevo
    nuevo_usuario = usuario(
        nombre=usuario,
        contrasena=clave,
        id_rol=rol_default.id_rol
    )

    db.session.add(nuevo_usuario)
    db.session.commit()
    return True



# ==========================
#  CLASE LOGIN MANAGER
# ==========================

class LoginManager:
    def login_system(self, app):

        # ==========
        # RUTA LOGIN
        # ==========
        def login():
            return render_template('login/struct.html')
        app.add_url_rule('/', 'login', login, methods=['GET'])

        # ==================
        # PROCESAR INICIO DE SESIÓN
        # ==================
        def iniciar_sesion():
            usuario = request.form.get('usuario', '').strip()
            clave = request.form.get('clave', '')

            if validar(usuario, clave):
                return render_template('home_panel/struct.html', usuario=usuario)

            return render_template(
                'login/login_invalid.html',
                error='Usuario o clave incorrectos.'
            )

        app.add_url_rule('/login', 'iniciar_sesion', iniciar_sesion, methods=['POST'])


        # ============
        # RUTA REGISTRO
        # ============
        def register():
            if request.method == 'GET':
                return render_template('login/register.html')

            # POST → registrar usuario
            usuario = request.form.get('usuario', '').strip()
            clave = request.form.get('clave', '')

            if registrar_usuario(usuario, clave):
                return render_template('login/register_success.html', usuario=usuario)
            else:
                return render_template('login/register.html', error='El usuario ya existe.')

        app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])


        # =====================
        # RUTAS DEL PANEL (EXISTENTES)
        # =====================
        def boleta():
            return render_template_string('<h1>Boleta de calificaciones</h1>')
        app.add_url_rule('/boleta', 'boleta', boleta)

        def constancia():
            return render_template_string('<h1>Constancia de estudio</h1>')
        app.add_url_rule('/constancia', 'constancia', constancia)

        def admin_alumnos():
            return render_template_string('<h1>Administración de alumnos</h1>')
        app.add_url_rule('/admin_alumnos', 'admin_alumnos', admin_alumnos)
