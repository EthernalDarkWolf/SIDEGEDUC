import sqlite3

DB_PATH = 'sidegeduc.db'
SQL_PATH = 'database/migration_parentescos.sql'

def aplicar_migracion():
    with open(SQL_PATH, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(sql)
        print('Migración aplicada correctamente.')
    except Exception as e:
        print('Error al aplicar la migración:', e)
    finally:
        conn.close()

if __name__ == '__main__':
    aplicar_migracion()
