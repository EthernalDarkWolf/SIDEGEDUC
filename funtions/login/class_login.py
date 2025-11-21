from flask import render_template, request, render_template_string

class LoginManager:
    def login_system(self, app):
        
        def login():
            return render_template('login/struct.html')
        app.add_url_rule('/', 'login', login, methods=['GET'])

      
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

       
        def register():
            if request.method == 'GET':
                return render_template('login/register.html')
            elif request.method == 'POST':
                if registrar_usuario is None:
                    return render_template('login/register.html', error='Registro no disponible.')

                usuario = request.form.get('usuario', '').strip()
                clave = request.form.get('clave', '')
                email = request.form.get('email', '').strip()

                try:
                    exito = registrar_usuario(usuario, clave, email)
                except Exception as e:
                    return render_template('login/register.html', error=f'Error en el registro: {str(e)}')

                if exito:
                    return render_template('login/register_success.html', usuario=usuario)
                else:
                    return render_template('login/register.html', error='El usuario ya existe.')

            
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