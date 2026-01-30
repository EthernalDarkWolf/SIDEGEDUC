from database.models import db, Roles, StatusUser, Sexo, TipoDocumento, Nacionalidad, Ciudades, EstadosCiviles, Religiones, NivelesAcademicos, Especialidades, Profesiones, Ocupaciones, Niveles, Grados, LetraSeccion, Cargos, Usuarios
from app import app
from werkzeug.security import generate_password_hash

def seed_database():
    with app.app_context():
        # Crear todas las tablas
        db.create_all()

        # Seed Roles
        if not Roles.query.first():
            roles = [
                Roles(id_rol=1, nombre_rol='Administrador'),
                Roles(id_rol=2, nombre_rol='Profesor'),
                Roles(id_rol=3, nombre_rol='Estudiante'),
                Roles(id_rol=4, nombre_rol='Representante'),
                Roles(id_rol=5, nombre_rol='Empleado')
            ]
            db.session.add_all(roles)

        # Seed StatusUser
        if not StatusUser.query.first():
            status = [
                StatusUser(id_status_user=1, estado='Activo'),
                StatusUser(id_status_user=2, estado='Inactivo'),
                StatusUser(id_status_user=3, estado='Suspendido')
            ]
            db.session.add_all(status)

        # Seed Sexo
        if not Sexo.query.first():
            sexos = [
                Sexo(id_sexo=1, letra_sexo='M'),
                Sexo(id_sexo=2, letra_sexo='F')
            ]
            db.session.add_all(sexos)

        # Seed TipoDocumento
        if not TipoDocumento.query.first():
            tipos_doc = [
                TipoDocumento(id_tipo_documento=1, nombre_tipo_documento='Cédula'),
                TipoDocumento(id_tipo_documento=2, nombre_tipo_documento='Pasaporte'),
                TipoDocumento(id_tipo_documento=3, nombre_tipo_documento='Licencia')
            ]
            db.session.add_all(tipos_doc)

        # Seed Nacionalidad
        if not Nacionalidad.query.first():
            paises = [
                Nacionalidad(id_pais=1, nombre_pais='Venezuela'),
                Nacionalidad(id_pais=2, nombre_pais='Colombia'),
                Nacionalidad(id_pais=3, nombre_pais='Estados Unidos'),
                Nacionalidad(id_pais=4, nombre_pais='España'),
                Nacionalidad(id_pais=5, nombre_pais='México')
            ]
            db.session.add_all(paises)

        # Seed Ciudades
        if not Ciudades.query.first():
            ciudades = [
                Ciudades(id_ciudad=1, nombre_ciudad='Caracas'),
                Ciudades(id_ciudad=2, nombre_ciudad='Bogotá'),
                Ciudades(id_ciudad=3, nombre_ciudad='Madrid'),
                Ciudades(id_ciudad=4, nombre_ciudad='Nueva York'),
                Ciudades(id_ciudad=5, nombre_ciudad='Ciudad de México')
            ]
            db.session.add_all(ciudades)

        # Seed EstadosCiviles
        if not EstadosCiviles.query.first():
            estados_civiles = [
                EstadosCiviles(id_estado_civil=1, descripcion_estado_civil='Soltero'),
                EstadosCiviles(id_estado_civil=2, descripcion_estado_civil='Casado'),
                EstadosCiviles(id_estado_civil=3, descripcion_estado_civil='Divorciado'),
                EstadosCiviles(id_estado_civil=4, descripcion_estado_civil='Viudo')
            ]
            db.session.add_all(estados_civiles)

        # Seed Religiones
        if not Religiones.query.first():
            religiones = [
                Religiones(id_religion=1, nombre_religion='Cristiano'),
                Religiones(id_religion=2, nombre_religion='Católico'),
                Religiones(id_religion=3, nombre_religion='Evangélico'),
                Religiones(id_religion=4, nombre_religion='Ateo'),
                Religiones(id_religion=5, nombre_religion='Otra')
            ]
            db.session.add_all(religiones)

        # Seed NivelesAcademicos
        if not NivelesAcademicos.query.first():
            niveles_academicos = [
                NivelesAcademicos(id_nivel_academico=1, nombre_nivel_academico='Primaria'),
                NivelesAcademicos(id_nivel_academico=2, nombre_nivel_academico='Secundaria'),
                NivelesAcademicos(id_nivel_academico=3, nombre_nivel_academico='Universitario'),
                NivelesAcademicos(id_nivel_academico=4, nombre_nivel_academico='Postgrado')
            ]
            db.session.add_all(niveles_academicos)

        # Seed Especialidades
        if not Especialidades.query.first():
            especialidades = [
                Especialidades(id_especialidad=1, nombre_especialidad='Matemáticas'),
                Especialidades(id_especialidad=2, nombre_especialidad='Lenguaje'),
                Especialidades(id_especialidad=3, nombre_especialidad='Ciencias'),
                Especialidades(id_especialidad=4, nombre_especialidad='Historia'),
                Especialidades(id_especialidad=5, nombre_especialidad='Educación Física')
            ]
            db.session.add_all(especialidades)

        # Seed Profesiones
        if not Profesiones.query.first():
            profesiones = [
                Profesiones(id_profesion=1, nombre_profesion='Ingeniero'),
                Profesiones(id_profesion=2, nombre_profesion='Médico'),
                Profesiones(id_profesion=3, nombre_profesion='Abogado'),
                Profesiones(id_profesion=4, nombre_profesion='Profesor'),
                Profesiones(id_profesion=5, nombre_profesion='Empresario')
            ]
            db.session.add_all(profesiones)

        # Seed Ocupaciones
        if not Ocupaciones.query.first():
            ocupaciones = [
                Ocupaciones(id_ocupacion=1, nombre_ocupacion='Empleado'),
                Ocupaciones(id_ocupacion=2, nombre_ocupacion='Independiente'),
                Ocupaciones(id_ocupacion=3, nombre_ocupacion='Estudiante'),
                Ocupaciones(id_ocupacion=4, nombre_ocupacion='Jubilado'),
                Ocupaciones(id_ocupacion=5, nombre_ocupacion='Ama de casa')
            ]
            db.session.add_all(ocupaciones)

        # Seed Niveles
        if not Niveles.query.first():
            niveles = [
                Niveles(id_nivel=1, nombre_nivel='Preescolar'),
                Niveles(id_nivel=2, nombre_nivel='Primaria'),
                Niveles(id_nivel=3, nombre_nivel='Secundaria'),
                Niveles(id_nivel=4, nombre_nivel='Media')
            ]
            db.session.add_all(niveles)

        # Seed Grados
        if not Grados.query.first():
            grados = [
                Grados(id_grado=1, numero_grado=1),
                Grados(id_grado=2, numero_grado=2),
                Grados(id_grado=3, numero_grado=3),
                Grados(id_grado=4, numero_grado=4),
                Grados(id_grado=5, numero_grado=5),
                Grados(id_grado=6, numero_grado=6)
            ]
            db.session.add_all(grados)

        # Seed LetraSeccion
        if not LetraSeccion.query.first():
            letras_seccion = [
                LetraSeccion(id_letra_seccion=1, letra='A'),
                LetraSeccion(id_letra_seccion=2, letra='B'),
                LetraSeccion(id_letra_seccion=3, letra='C'),
                LetraSeccion(id_letra_seccion=4, letra='D')
            ]
            db.session.add_all(letras_seccion)

        # Seed Cargos
        if not Cargos.query.first():
            cargos = [
                Cargos(id_cargo=1, nombre_cargo='Director'),
                Cargos(id_cargo=2, nombre_cargo='Secretario'),
                Cargos(id_cargo=3, nombre_cargo='Tesorero'),
                Cargos(id_cargo=4, nombre_cargo='Coordinador'),
                Cargos(id_cargo=5, nombre_cargo='Auxiliar')
            ]
            db.session.add_all(cargos)

        # Crear usuario administrador por defecto
        admin_exists = Usuarios.query.filter_by(nombre='admin').first()
        if not admin_exists:
            admin_user = Usuarios(
                nombre='admin',
                contrasena=generate_password_hash('admin123'),
                id_rol=1,
                id_status_user=1
            )
            db.session.add(admin_user)

        try:
            db.session.commit()
            print("Base de datos poblada exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"Error al poblar la base de datos: {e}")

if __name__ == '__main__':
    seed_database()