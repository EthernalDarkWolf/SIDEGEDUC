import sqlite3
import os

# Ruta correcta al archivo sidegeduc.db en la raíz del proyecto
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sidegeduc.db'))

alter_commands = [
    "ALTER TABLE personas ADD COLUMN id_tipo_persona INTEGER",
    "ALTER TABLE personas ADD COLUMN id_tipo_documento INTEGER",
    "ALTER TABLE personas ADD COLUMN numero_cedula TEXT",
    "ALTER TABLE personas ADD COLUMN id_ocupacion INTEGER",
    "ALTER TABLE personas ADD COLUMN id_profesion INTEGER",
    "ALTER TABLE personas ADD COLUMN num_hijos INTEGER",
    "ALTER TABLE personas ADD COLUMN id_relacion_familiar INTEGER"
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for cmd in alter_commands:
    try:
        c.execute(cmd)
        print(f'OK: {cmd}')
    except Exception as e:
        print(f'Ya existe o error: {cmd} -> {e}')

conn.commit()
conn.close()
print('Actualización de tabla personas completada.')
