# Crear tablas referenciadas por claves foráneas si no existen
CREATE_SEXO_SQL = '''
CREATE TABLE IF NOT EXISTS sexo (
    id_sexo INTEGER PRIMARY KEY AUTOINCREMENT,
    letra_sexo TEXT NOT NULL
);
'''
CREATE_TIPO_PERSONA_SQL = '''
CREATE TABLE IF NOT EXISTS tipo_persona (
    id_tipo_persona INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_tipo_persona TEXT NOT NULL
);
'''
CREATE_TIPO_DOCUMENTO_SQL = '''
CREATE TABLE IF NOT EXISTS tipo_documento (
    id_tipo_documento INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
);
'''
CREATE_OCUPACIONES_SQL = '''
CREATE TABLE IF NOT EXISTS ocupaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
);
'''
CREATE_PROFESIONES_SQL = '''
CREATE TABLE IF NOT EXISTS profesiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
);
'''
CREATE_RELACIONES_FAMILIARES_SQL = '''
CREATE TABLE IF NOT EXISTS relaciones_familiares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
);
'''
import sqlite3

# Ruta a la base de datos
DB_PATH = 'sidegeduc.db'
DROP_NIVELESACADEMICOS_SQL = 'DROP TABLE IF EXISTS niveles_academicos;'
DROP_ESTADOSCIVILES_SQL = 'DROP TABLE IF EXISTS estados_civiles;'

# Esquema correcto para la tabla personas
CREATE_NIVEL_INSTRUCCION_SQL = '''
CREATE TABLE IF NOT EXISTS nivel_instruccion (
    id_nivel_instruccion INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
);
'''
CREATE_HIJOPOSICION_SQL = '''
CREATE TABLE IF NOT EXISTS posicion_de_hijo (
    id_posicion_de_hijo INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
);
'''

CREATE_PERSONAS_SQL = '''
CREATE TABLE IF NOT EXISTS personas (
    id_persona INTEGER PRIMARY KEY AUTOINCREMENT,
    primer_nombre TEXT NOT NULL,
    segundo_nombre TEXT,
    primer_apellido TEXT NOT NULL,
    segundo_apellido TEXT,
    fecha_nacimiento TEXT,
    id_sexo INTEGER,
    id_tipo_persona INTEGER NOT NULL,
    id_tipo_documento INTEGER,
    numero_cedula TEXT,
    id_ocupacion INTEGER,
    id_profesion INTEGER,
    num_hijos INTEGER,
    id_relacion_familiar INTEGER,
    FOREIGN KEY (id_sexo) REFERENCES sexo(id_sexo),
    FOREIGN KEY (id_tipo_persona) REFERENCES tipo_persona(id_tipo_persona),
    FOREIGN KEY (id_tipo_documento) REFERENCES tipo_documento(id_tipo_documento),
    FOREIGN KEY (id_ocupacion) REFERENCES ocupaciones(id),
    FOREIGN KEY (id_profesion) REFERENCES profesiones(id),
    FOREIGN KEY (id_relacion_familiar) REFERENCES relaciones_familiares(id)
);
'''

# Elimina la tabla personas si existe
DROP_PERSONAS_SQL = 'DROP TABLE IF EXISTS personas;'

# DROP TABLES FORÁNEAS
DROP_SEXO_SQL = 'DROP TABLE IF EXISTS sexo;'
DROP_TIPO_PERSONA_SQL = 'DROP TABLE IF EXISTS tipo_persona;'
DROP_TIPO_DOCUMENTO_SQL = 'DROP TABLE IF EXISTS tipo_documento;'
DROP_OCUPACIONES_SQL = 'DROP TABLE IF EXISTS ocupaciones;'
DROP_PROFESIONES_SQL = 'DROP TABLE IF EXISTS profesiones;'
DROP_RELACIONES_FAMILIARES_SQL = 'DROP TABLE IF EXISTS relaciones_familiares;'

# Registro de prueba

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Mostrar estructura actual de la tabla personas si existe
    try:
        cursor.execute("PRAGMA table_info(personas);")
        columns = cursor.fetchall()
        if columns:
            print("Estructura actual de la tabla personas:")
            for col in columns:
                print(col)
        else:
            print("La tabla personas no existe actualmente.")
    except Exception as e:
        print("Error al consultar la estructura de personas:", e)
    try:
        cursor.execute(DROP_PERSONAS_SQL)
        cursor.execute(DROP_SEXO_SQL)
        cursor.execute(DROP_TIPO_PERSONA_SQL)
        cursor.execute(DROP_TIPO_DOCUMENTO_SQL)
        cursor.execute(DROP_OCUPACIONES_SQL)
        cursor.execute(DROP_PROFESIONES_SQL)
        cursor.execute(DROP_RELACIONES_FAMILIARES_SQL)
        # Crear tablas base primero
        cursor.execute(CREATE_SEXO_SQL)
        cursor.execute(CREATE_TIPO_PERSONA_SQL)
        cursor.execute(CREATE_TIPO_DOCUMENTO_SQL)
        cursor.execute(CREATE_OCUPACIONES_SQL)
        cursor.execute(CREATE_PROFESIONES_SQL)
        cursor.execute(CREATE_RELACIONES_FAMILIARES_SQL)
        # Crear tabla personas
        cursor.execute(CREATE_PERSONAS_SQL)
        # Insertar datos válidos en todas las tablas foráneas
        cursor.execute("INSERT OR IGNORE INTO sexo (letra_sexo) VALUES ('M'), ('F')")
        cursor.execute("INSERT OR IGNORE INTO tipo_persona (nombre_tipo_persona) VALUES ('estudiante'), ('profesor'), ('representante'), ('empleado')")
        cursor.execute("INSERT OR IGNORE INTO tipo_documento (nombre) VALUES ('Cédula Nacional'), ('Cédula Escolar')")
        cursor.execute("INSERT OR IGNORE INTO ocupaciones (nombre) VALUES ('Oficios del hogar'), ('Obrero'), ('Independiente'), ('Empleado público')")
        cursor.execute("INSERT OR IGNORE INTO profesiones (nombre) VALUES ('Doctorado'), ('Técnico Superior Universitario'), ('Licenciado'), ('Ingeniero')")
        cursor.execute("INSERT OR IGNORE INTO relaciones_familiares (nombre) VALUES ('Padre'), ('Madre'), ('Representante'), ('Tutor')")
        conn.commit()
        print('Tablas base y tabla personas recreadas. Datos foráneos insertados.')
    except Exception as e:
        print('Error:', e)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
