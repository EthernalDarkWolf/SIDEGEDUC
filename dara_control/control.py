from typing import Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash
from conn import get_connection

ROLES = ("Desarrollador", "Profesor", "Estudiante")

def registrar(nombre: str, email: Optional[str], clave: str, rol: str = "Estudiante") -> Tuple[bool, Optional[str]]:
    if not nombre or not clave:
        return False, "Nombre y clave requeridos"
    if rol not in ROLES:
        return False, "Rol inválido"
    hashed = generate_password_hash(clave)
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO usuarios (nombre, email, clave, rol) VALUES (%s, %s, %s, %s)",
            (nombre, email, hashed, rol)
        )
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        if conn:
            conn.close()

def validar(nombre: str, clave: str) -> bool:
    if not nombre or not clave:
        return False
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT clave FROM usuarios WHERE nombre = %s", (nombre,))
        row = cur.fetchone()
        if not row:
            return False
        return check_password_hash(row[0], clave)
    except Exception:
        return False
    finally:
        if conn:
            conn.close()

def obtener_usuario(nombre: str):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, email, rol, creado FROM usuarios WHERE nombre = %s", (nombre,))
        return cur.fetchone()  # (id, nombre, email, rol, creado) or None
    finally:
        if conn:
            conn.close()