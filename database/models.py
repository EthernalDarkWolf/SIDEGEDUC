

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Modelo para tipos de persona (wizard)
class TipoPersona(db.Model):
    __tablename__ = 'tipo_persona'
    id_tipo_persona = db.Column(db.Integer, primary_key=True)
    nombre_tipo_persona = db.Column(db.String(50), unique=True, nullable=False)

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
    id_user = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False)
    id_status_user = db.Column(db.Integer, db.ForeignKey('status_user.id_status_user'), nullable=False)

class Sexo(db.Model):
    __tablename__ = 'sexo'
    id_sexo = db.Column(db.Integer, primary_key=True)
    letra_sexo = db.Column(db.String(1), unique=True, nullable=False)

class TipoDocumento(db.Model):
    __tablename__ = 'tipo_documento'
    id_tipo_documento = db.Column(db.Integer, primary_key=True)
    nombre_tipo_documento = db.Column(db.String(50), unique=True, nullable=False)

class Nacionalidad(db.Model):
    __tablename__ = 'nacionalidad'
    id_pais = db.Column(db.Integer, primary_key=True)
    nombre_pais = db.Column(db.String(100), unique=True, nullable=False)

class Ciudades(db.Model):
    __tablename__ = 'ciudades'
    id_ciudad = db.Column(db.Integer, primary_key=True)
    nombre_ciudad = db.Column(db.String(100), unique=True, nullable=False)

class Direcciones(db.Model):
    __tablename__ = 'direcciones'
    id_direccion = db.Column(db.Integer, primary_key=True)
    direccion = db.Column(db.Text, nullable=False)
    id_ciudad = db.Column(db.Integer, db.ForeignKey('ciudades.id_ciudad'))
    id_pais = db.Column(db.Integer, db.ForeignKey('nacionalidad.id_pais'))

class Contactos(db.Model):
    __tablename__ = 'contactos'
    id_contacto = db.Column(db.Integer, primary_key=True)
    telefono = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

class EstadosCiviles(db.Model):
    __tablename__ = 'estados_civiles'
    id_estado_civil = db.Column(db.Integer, primary_key=True)
    descripcion_estado_civil = db.Column(db.String(50), unique=True, nullable=False)

class Religiones(db.Model):
    __tablename__ = 'religiones'
    id_religion = db.Column(db.Integer, primary_key=True)
    nombre_religion = db.Column(db.String(100), unique=True, nullable=False)

class NivelesAcademicos(db.Model):
    __tablename__ = 'niveles_academicos'
    id_nivel_academico = db.Column(db.Integer, primary_key=True)
    nombre_nivel_academico = db.Column(db.String(100), unique=True, nullable=False)

class Especialidades(db.Model):
    __tablename__ = 'especialidades'
    id_especialidad = db.Column(db.Integer, primary_key=True)
    nombre_especialidad = db.Column(db.String(100), unique=True, nullable=False)

class Profesiones(db.Model):
    __tablename__ = 'profesiones'
    id_profesion = db.Column(db.Integer, primary_key=True)
    nombre_profesion = db.Column(db.String(100), unique=True, nullable=False)

class Ocupaciones(db.Model):
    __tablename__ = 'ocupaciones'
    id_ocupacion = db.Column(db.Integer, primary_key=True)
    nombre_ocupacion = db.Column(db.String(100), unique=True, nullable=False)

class Niveles(db.Model):
    __tablename__ = 'niveles'
    id_nivel = db.Column(db.Integer, primary_key=True)
    nombre_nivel = db.Column(db.String(50), unique=True, nullable=False)

class Grados(db.Model):
    __tablename__ = 'grados'
    id_grado = db.Column(db.Integer, primary_key=True)
    numero_grado = db.Column(db.Integer, unique=True, nullable=False)

class LetraSeccion(db.Model):
    __tablename__ = 'letra_seccion'
    id_letra_seccion = db.Column(db.Integer, primary_key=True)
    letra = db.Column(db.String(1), unique=True, nullable=False)

class Secciones(db.Model):
    __tablename__ = 'secciones'
    id_seccion = db.Column(db.Integer, primary_key=True)
    id_letra_seccion = db.Column(db.Integer, db.ForeignKey('letra_seccion.id_letra_seccion'))
    id_grado = db.Column(db.Integer, db.ForeignKey('grados.id_grado'))
    id_nivel = db.Column(db.Integer, db.ForeignKey('niveles.id_nivel'))

class Materias(db.Model):
    __tablename__ = 'materias'
    id_materia = db.Column(db.Integer, primary_key=True)
    nombre_materia = db.Column(db.String(100), unique=True, nullable=False)

class Cargos(db.Model):
    __tablename__ = 'cargos'
    id_cargo = db.Column(db.Integer, primary_key=True)
    nombre_cargo = db.Column(db.String(100), unique=True, nullable=False)

class Planteles(db.Model):
    __tablename__ = 'planteles'
    id_plantel = db.Column(db.Integer, primary_key=True)
    nombre_plantel_nomina = db.Column(db.String(200))
    codigo_pa = db.Column(db.String(100), unique=True)
    # Additional columns exist in schema but are optional; include if needed
    # id_nivel = db.Column(db.Integer, db.ForeignKey('niveles.id_nivel'))
    # id_cargo = db.Column(db.Integer, db.ForeignKey('cargos.id_cargo'))

class Personas(db.Model):
    __tablename__ = 'personas'
    id_persona = db.Column(db.Integer, primary_key=True)
    primer_nombre = db.Column(db.String(50), nullable=False)
    segundo_nombre = db.Column(db.String(50))
    primer_apellido = db.Column(db.String(50), nullable=False)
    segundo_apellido = db.Column(db.String(50))
    fecha_nacimiento = db.Column(db.Date)
    id_sexo = db.Column(db.Integer, db.ForeignKey('sexo.id_sexo'))

class UsuarioPersona(db.Model):
    __tablename__ = 'usuario_persona'
    id_usuario_persona = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('usuarios.id_user'))
    id_persona = db.Column(db.Integer, db.ForeignKey('personas.id_persona'))

class Estudiantes(db.Model):
    __tablename__ = 'estudiantes'
    id_estudiante = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('personas.id_persona'))
    fecha_inscripcion = db.Column(db.Date, nullable=False)

class Profesores(db.Model):
    __tablename__ = 'profesores'
    id_profesor = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('personas.id_persona'))
    id_especialidad = db.Column(db.Integer, db.ForeignKey('especialidades.id_especialidad'))

class Empleados(db.Model):
    __tablename__ = 'empleados'
    id_empleado = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('personas.id_persona'))
    id_cargo = db.Column(db.Integer, db.ForeignKey('cargos.id_cargo'))
    fecha_contratacion = db.Column(db.Date)
    salario = db.Column(db.Numeric(10, 2))

class Representantes(db.Model):
    __tablename__ = 'representantes'
    id_representante = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('personas.id_persona'))
    id_profesion = db.Column(db.Integer, db.ForeignKey('profesiones.id_profesion'))
    id_ocupacion = db.Column(db.Integer, db.ForeignKey('ocupaciones.id_ocupacion'))
    id_nivel_academico = db.Column(db.Integer, db.ForeignKey('niveles_academicos.id_nivel_academico'))
