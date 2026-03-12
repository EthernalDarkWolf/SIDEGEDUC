import sqlite3

# Ruta de la base de datos
DB_PATH = 'sidegeduc.db'

# Datos iniciales
relaciones = [
    ('Padre',),
    ('Madre',),
    ('Representante',),
    ('Tutor legal',),
    ('Hermano',),
    ('Hermana',),
    ('Otro',)
]

# Crear tabla y poblarla
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS relaciones_familiares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
);
''')
cursor.executemany('INSERT OR IGNORE INTO relaciones_familiares (nombre) VALUES (?)', relaciones)
conn.commit()
conn.close()
print('Tabla relaciones_familiares creada y poblada.')
