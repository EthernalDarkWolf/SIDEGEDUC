from flask import Flask
from utiled.Login import LoginManager
from database.Models import models


app = Flask(__name__)
#Llamar la clase para el login del sistema y todas sus funcopnesnes 
LoginManager().login_system(app)



if __name__ == '__main__':
    app.run(debug=True)