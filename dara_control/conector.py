from conn import get_connection
from mysql.connector import Error

def create_connection():
    try:
        conn = get_connection()
        if conn and conn.is_connected():
            print("Connection to MySQL DB successful")
            return conn
    except Error as e:
        print(f"The error '{e}' occurred")
    return None