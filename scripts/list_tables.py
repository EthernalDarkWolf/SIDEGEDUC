import sqlite3

if __name__ == '__main__':
    db_path = r'c:/Proyectos/SIDEGEDUC/sidegeduc.db'
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    print('tables:', tables)
    conn.close()
