from flask import Flask, render_template, request
from users_and_rols.users import usuarios

app = Flask(__name__)


#cargar el esquema de entrada (login):
@app.route('/')
def index():
    return render_template(login.html)

@app.route('/login', methods=['GET', 'POST'])# ruta para evitar el error 404 en el login



#procesar y renderizar el otro esquema
@app.route('/login', methods=['POST'])
def login():
    usario = request.form['user']
    clave = request.form['pw']
    if usuarios.get(usuario) == clave:
        return render_template('panel.html', usuario=usuario)
    else:
        print("Error Usuario o clave incorrectos")

if __name__ == '__main__':
    app.run(debug=True)