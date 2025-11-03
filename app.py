from flask import Flask, render_template, request, redirect, url_for

from usuarios.users import validar

app = Flask(__name__) 


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def iniciar_sesion():
    # uso de .get() para evitar KeyError y normalizar input
    usuario = request.form.get('usuario', '').strip()
    clave = request.form.get('clave', '')
    # validar debe devolver True/False; proteger contra excepciones internas
    try:
        valido = validar(usuario, clave)
    except Exception:
        valido = False

    if valido:
        # renderiza panel.html pasando el usuario al template
        return render_template('panel.html', usuario=usuario)
    else:
        return "Credenciales inválidas", 401


if __name__ == '__main__':
    app.run(debug=True)