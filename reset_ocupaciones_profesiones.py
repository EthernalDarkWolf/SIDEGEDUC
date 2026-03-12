import sqlite3

DB_PATH = 'sidegeduc.db'

# Eliminar tablas si existen
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS ocupaciones')
cursor.execute('DROP TABLE IF EXISTS profesiones')
conn.commit()

# Crear tablas nuevas
cursor.execute('''
CREATE TABLE ocupaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
)
''')
cursor.execute('''
CREATE TABLE profesiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
)
''')

# Datos iniciales
ocupaciones = [
    ('Oficios del hogar',),
    ('Estudiante',),
    ('Empleado',),
    ('Desempleado/a',),
    ('Jubilado/a',),
    ('Otro',),
]
profesiones = [
    ('Sin educación formal',),
    ('Primaria',),
    ('Bachillerato',),
    ('Universitario',),
    ('Técnico Superior Universitario',),
    ('Ingeniero',),
    ('Posgrado',),
    ('Doctorado',),
    ('Otro',),
    ]
cursor.executemany('INSERT INTO ocupaciones (nombre) VALUES (?)', ocupaciones)
cursor.executemany('INSERT INTO profesiones (nombre) VALUES (?)', profesiones)
conn.commit()
conn.close()
print('Tablas ocupaciones y profesiones recreadas y pobladas correctamente.')
