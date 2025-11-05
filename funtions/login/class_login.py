from flask import render_template, request, render_template_string
from usuarios.users import validar
try:
    from usuarios.users import registrar as registrar_usuario
except Exception:
    registrar_usuario = None

class LoginManager:
    def register(self, app):
        # GET /
        def login():
            return render_template('login/struct.html')
        app.add_url_rule('/', 'login', login, methods=['GET'])

        # POST /login
        def iniciar_sesion():
            usuario = request.form.get('usuario', '').strip()
            clave = request.form.get('clave', '')
            try:
                valido = validar(usuario, clave)
            except Exception:
                valido = False

            if valido:
                return render_template('home_panel/struct.html', usuario=usuario)
            return render_template('login/login_invalid.html', error='Usuario o clave incorrectos.')
        app.add_url_rule('/login', 'iniciar_sesion', iniciar_sesion, methods=['POST'])

        # GET+POST /register
        def register():
            if request.method == 'GET':
                return render_template('login/register.html')
            nombre = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            clave = request.form.get('password', '')
            if not nombre or not clave:
                return render_template('login/register.html', error='Nombre y clave requeridos.')
            if registrar_usuario:
                ok, msg = registrar_usuario(nombre, email, clave)
                if ok:
                    return render_template('home_panel/struct.html', usuario=nombre)
                return render_template('login/register.html', error=msg)
            return render_template('home_panel/struct.html', usuario=nombre)
        app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])

        # Rutas del panel (evitan BuildError en templates)
        def boleta():
            return render_template_string(
                '<h1>Boleta de calificaciones</h1><p>Contenido pendiente...</p>'
                '<p><a href="{{ url_for(\'login\') }}">Volver</a></p>'
            )
        app.add_url_rule('/boleta', 'boleta', boleta, methods=['GET'])

        def constancia():
            return render_template_string(
                '<h1>Constancia de estudio</h1><p>Contenido pendiente...</p>'
                '<p><a href="{{ url_for(\'login\') }}">Volver</a></p>'
            )
        app.add_url_rule('/constancia', 'constancia', constancia, methods=['GET'])

        def admin_alumnos():
            return render_template_string(
                '<h1>Administración de alumnos</h1><p>Contenido pendiente...</p>'
                '<p><a href="{{ url_for(\'login\') }}">Volver</a></p>'
            )
        app.add_url_rule('/admin_alumnos', 'admin_alumnos', admin_alumnos, methods=['GET'])