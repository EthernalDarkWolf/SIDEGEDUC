"""Recrear tabla `representantes` en la base de datos SQLite.

Este script está diseñado para ejecutarse en el mismo directorio donde se
encuentra el archivo `sidegeduc.db` (misma ubicación que `app.py`).

Uso:
    python recrear_personas.py
"""

import os
import sqlite3

# Ruta a la base de datos (misma que usa la aplicación Flask)
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sidegeduc.db'))

DDL = [
    # Borrar tabla si existe para recrearla desde cero
    "DROP TABLE IF EXISTS representantes;",

    # Crear tabla de representantes con las llaves foráneas correctas
    """
    CREATE TABLE IF NOT EXISTS representantes (
        id_representante INTEGER NOT NULL PRIMARY KEY,
        id_persona INTEGER,
        id_profesion INTEGER,
        id_ocupacion INTEGER,
        id_nivel_academico INTEGER,
        FOREIGN KEY(id_persona) REFERENCES personas(id_persona),
        FOREIGN KEY(id_profesion) REFERENCES profesiones(id),
        FOREIGN KEY(id_ocupacion) REFERENCES ocupaciones(id),
        FOREIGN KEY(id_nivel_academico) REFERENCES niveles_academicos(id_nivel_academico)
    );
    """,
]


def main():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"No se encontró la base de datos SQLite en: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor = conn.cursor()
        for stmt in DDL:
            cursor.executescript(stmt)
            print(f"Ejecutado: {stmt.strip().splitlines()[0]}")
        conn.commit()
        print('Tabla `representantes` recreada correctamente.')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
