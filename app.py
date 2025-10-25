from flask import Flask, render_template, request

from users_and_rols.users import usuarios

app = Flask(__name__)


# cargar el esquema de entrada (login)
@app.route('/', methods=['GET'])
def index():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # si es GET, se muestra el formulario directo en /login.html
    if request.method == 'GET':
        return render_template('login.html')

    # Variables para procesar usuario y contraseña:
    usuario = request.form.get('user', '')
    clave = request.form.get('pw', '')

    # usuarios almacenados usan números, por eso se compara como string:
    stored = usuarios.get(usuario)

    if stored is not None and str(stored) == str(clave):
        # autenticación correcta: renderizamos panel con el usuario
        return render_template('panel.html', usuario=usuario)
    else:
        # autenticación fallida:regresa login mostrando un mensaje de error:
        return render_template('login.html', error="Usuario o clave incorrectos")

#esto de abajo es para que corra todo lo del archivo al ejecutarlo:
if __name__ == '__main__':
    app.run(debug=True)
