# ...existing code...
# Diccionario de ejemplo: ajustar nombres/contraseñas reales aquí
usuarios = {
    'Anthony': '1234',
}

def validar(usuario, clave):
    """
    Devuelve True si el usuario existe en el diccionario y la clave coincide.
    Protege contra None y tipos incorrectos.
    """
    if not isinstance(usuario, str) or not isinstance(clave, str):
        return False
    usuario = usuario.strip()
    if not usuario or not clave:
        return False
    return usuarios.get(usuario) == clave
