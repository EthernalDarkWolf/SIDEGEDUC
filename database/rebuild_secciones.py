#!/usr/bin/env python3
"""Script de mantenimiento: recrea/rehabilita las tablas necesarias para gestionar secciones.

Uso:
  python database/rebuild_secciones.py --seed
  python database/rebuild_secciones.py --reset
  python database/rebuild_secciones.py --reset --seed

Este script es útil cuando la página de creación de secciones muestra selects vacíos
porque las tablas de `niveles`, `grados` o `letra_seccion` no tienen datos.

Nota: eliminará (drop) las tablas listadas cuando se utilice --reset.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(ROOT_DIR, 'sidegeduc.db')

DEFAULT_NIVELES = ['Preescolar', 'Primaria', 'Secundaria']
DEFAULT_GRADOS = list(range(1, 7))
DEFAULT_LETRAS = ['A', 'B', 'C', 'D', 'E', 'F']


def connect(db_path: str) -> sqlite3.Connection:
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"No se encontró la base de datos en: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    """Crea las tablas necesarias para el módulo de secciones."""
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS niveles (
            id_nivel INTEGER PRIMARY KEY,
            nombre_nivel TEXT NOT NULL UNIQUE
        )
        '''
    )
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS grados (
            id_grado INTEGER PRIMARY KEY,
            numero_grado INTEGER NOT NULL UNIQUE
        )
        '''
    )
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS letra_seccion (
            id_letra_seccion INTEGER PRIMARY KEY,
            letra TEXT NOT NULL UNIQUE
        )
        '''
    )
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS secciones (
            id_seccion INTEGER PRIMARY KEY,
            id_letra_seccion INTEGER,
            id_grado INTEGER,
            id_nivel INTEGER,
            FOREIGN KEY (id_letra_seccion) REFERENCES letra_seccion(id_letra_seccion),
            FOREIGN KEY (id_grado) REFERENCES grados(id_grado),
            FOREIGN KEY (id_nivel) REFERENCES niveles(id_nivel)
        )
        '''
    )
    conn.commit()


def drop_tables(conn: sqlite3.Connection) -> None:
    """Elimina las tablas relacionadas a secciones (utilizar con cuidado)."""
    conn.execute('PRAGMA foreign_keys = OFF')
    for table in ['secciones', 'letra_seccion', 'grados', 'niveles']:
        conn.execute(f'DROP TABLE IF EXISTS {table}')
    conn.execute('PRAGMA foreign_keys = ON')
    conn.commit()


def seed_defaults(conn: sqlite3.Connection) -> None:
    """Inserta datos iniciales (niveles, grados, letras)."""
    for idx, nombre in enumerate(DEFAULT_NIVELES, start=1):
        conn.execute(
            'INSERT OR IGNORE INTO niveles (id_nivel, nombre_nivel) VALUES (?, ?)',
            (idx, nombre),
        )

    for numero in DEFAULT_GRADOS:
        conn.execute(
            'INSERT OR IGNORE INTO grados (id_grado, numero_grado) VALUES (?, ?)',
            (numero, numero),
        )

    for idx, letra in enumerate(DEFAULT_LETRAS, start=1):
        conn.execute(
            'INSERT OR IGNORE INTO letra_seccion (id_letra_seccion, letra) VALUES (?, ?)',
            (idx, letra),
        )

    conn.commit()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Recrea / rellena tablas para el módulo secciones')
    p.add_argument('--reset', action='store_true', help='Borrar y volver a crear las tablas (perder datos)')
    p.add_argument('--seed', action='store_true', help='Insertar datos iniciales (niveles, grados, letras)')
    p.add_argument('--db', default=DB_PATH, help='Ruta al archivo SQLite (por defecto: sidegeduc.db)')
    return p.parse_args()


def main() -> int:
    args = parse_args()

    try:
        conn = connect(args.db)
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        return 1

    try:
        if args.reset:
            print('🔄 Borrando tablas de secciones...')
            drop_tables(conn)
            print('✅ Tablas borradas.')

        print('✅ Asegurando que las tablas existen...')
        create_tables(conn)

        if args.seed:
            print('🌱 Insertando datos iniciales en niveles/grados/letras...')
            seed_defaults(conn)
            print('✅ Datos iniciales insertados.')

        print('✅ Operación completada con éxito.')
        return 0
    except Exception as e:
        print(f'ERROR durante la operación: {e}', file=sys.stderr)
        return 2
    finally:
        conn.close()


if __name__ == '__main__':
    raise SystemExit(main())
