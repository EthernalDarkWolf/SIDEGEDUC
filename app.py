from flask import Flask, render_template, request, redirect, url_for

from usuarios.users import validar

app = Flask(__name__) 


@app.route('/')
def login():
    return render_template('login/struct.html')

@app.route('/login', methods=['POST'])
def iniciar_sesion():
    usuario = request.form.get('usuario', '').strip()
    clave = request.form.get('clave', '')
    try:
        valido = validar(usuario, clave)
    except Exception:
        valido = False

    if valido:
        return render_template('home_panel/struct.html', usuario=usuario)
    else:
        return render_template('login/login_invalid.html', error='Usuario o clave incorrectos.')


@app.route('/boleta')
def boleta():
    return render_template('home_panel/boleta.html')

@app.route('/constancia')
def constancia():
    return render_template('home_panel/constancia.html')

@app.route('/admin_alumnos')
def admin_alumnos():
    return render_template('home_panel/admin_alumnos.html')

if __name__ == '__main__':
    app.run(debug=True)