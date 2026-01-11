from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Roles(db.Model):
    __tablename__ = 'roles'
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50), unique=True, nullable=False)

class StatusUser(db.Model):
    __tablename__ = 'status_user'
    id_status_user = db.Column(db.Integer, primary_key=True)
    estado = db.Column(db.String(50), unique=True, nullable=False)

class Usuarios(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False)
    id_status_user = db.Column(db.Integer, db.ForeignKey('status_user.id_status_user'), nullable=False)
