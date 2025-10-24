from flask import Flask, render_template, request

from users_and_rols.users import usuarios

app = Flask(__name__)


# cargar el esquema de entrada (login)
@app.route('/', methods=['GET'])
def index():
    # usar cadena con el nombre del archivo de plantilla
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # si es GET, mostramos el formulario (por si se accede directamente a /login)
    if request.method == 'GET':
        return render_template('login.html')

    # POST: procesar credenciales
    usuario = request.form.get('user', '')
    clave = request.form.get('pw', '')

    # usuarios almacenados usan números, por eso comparamos como strings
    stored = usuarios.get(usuario)

    if stored is not None and str(stored) == str(clave):
        # autenticación correcta: renderizamos panel con el usuario
        return render_template('panel.html', usuario=usuario)
    else:
        # autenticación fallida: volvemos al login mostrando un mensaje de error
        # (no modificamos tu CSS/HTML; si quieres puedo añadir la plantilla para mostrar error)
        return render_template('login.html', error="Usuario o clave incorrectos")


if __name__ == '__main__':
    app.run(debug=True)
