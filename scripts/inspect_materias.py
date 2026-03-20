import sqlite3

if __name__ == '__main__':
    db_path = r'c:/Proyectos/SIDEGEDUC/sidegeduc.db'
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    print('schema:', cur.execute("PRAGMA table_info(materias)").fetchall())
    print('rows:', cur.execute("SELECT id_materia, nombre_materia FROM materias").fetchall())
    conn.close()
