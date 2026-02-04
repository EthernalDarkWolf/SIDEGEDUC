import os
import sys

# Añadir el directorio actual al path para evitar errores de importación
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    # Intento 1: Importar desde la carpeta database (si existe)
    from database.models import (
        db, Roles, StatusUser, Sexo, TipoDocumento, Nacionalidad, 
        Ciudades, EstadosCiviles, Religiones, NivelesAcademicos, 
        Especialidades, Profesiones, Ocupaciones, Niveles, Grados, 
        LetraSeccion, Cargos, Usuarios
    )
except ImportError:
    # Intento 2: Importar directamente si está en la raíz
    from models import (
        db, Roles, StatusUser, Sexo, TipoDocumento, Nacionalidad, 
        Ciudades, EstadosCiviles, Religiones, NivelesAcademicos, 
        Especialidades, Profesiones, Ocupaciones, Niveles, Grados, 
        LetraSeccion, Cargos, Usuarios
    )

from app import app
from werkzeug.security import generate_password_hash

def seed_database():
    with app.app_context():
        try:
            print("--- Iniciando poblado de base de datos ---")
            
            # Crear todas las tablas en el archivo .db
            db.create_all()

            # --- SEED DATA ---
            # 1. Roles
            if not Roles.query.first():
                db.session.add_all([
                    Roles(id_rol=1, nombre_rol='Administrador'),
                    Roles(id_rol=2, nombre_rol='Profesor'),
                    Roles(id_rol=3, nombre_rol='Estudiante'),
                    Roles(id_rol=4, nombre_rol='Representante'),
                    Roles(id_rol=5, nombre_rol='Empleado'),
                    # Rol especial superior: Creador (invisible para el resto)
                    Roles(id_rol=99, nombre_rol='Creador')
                ])
                print("Roles creados.")

            # 2. StatusUser
            if not StatusUser.query.first():
                db.session.add_all([
                    StatusUser(id_status_user=1, estado='Activo'),
                    StatusUser(id_status_user=2, estado='Inactivo'),
                    StatusUser(id_status_user=3, estado='Suspendido')
                ])
                print("Estados creados.")

            # 3. Sexo
            if not Sexo.query.first():
                db.session.add_all([Sexo(id_sexo=1, letra_sexo='M'), Sexo(id_sexo=2, letra_sexo='F')])
                print("Sexos creados.")

            # 4. TipoDocumento
            if not TipoDocumento.query.first():
                db.session.add_all([
                    TipoDocumento(id_tipo_documento=1, nombre_tipo_documento='Cédula'),
                    TipoDocumento(id_tipo_documento=2, nombre_tipo_documento='Pasaporte'),
                    TipoDocumento(id_tipo_documento=3, nombre_tipo_documento='Licencia')
                ])
                print("Tipos de documento creados.")

            # 5. Usuario Administrador (IMPORTANTE)
            # Verifica si ya existe para no duplicar
            admin_user = Usuarios.query.filter_by(nombre='admin').first()
            if not admin_user:
                nuevo_admin = Usuarios(
                    nombre='admin',
                    contrasena=generate_password_hash('admin123'),
                    id_rol=1,
                    id_status_user=1
                )
                db.session.add(nuevo_admin)
                print("Usuario 'admin' creado exitosamente.")

            db.session.commit()
            print("--- Proceso completado con éxito ---")
            print("Clave de acceso: admin / admin123")

        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")

if __name__ == '__main__':
    seed_database()