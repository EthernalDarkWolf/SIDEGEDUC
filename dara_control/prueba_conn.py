from conn import get_connection
try:
    c = get_connection()
    print("Conectado:", c.is_connected())
    c.close()
except Exception as e:
    print("MySQL ERROR:", type(e).__name__, e)