from .users import registrar, validar, obtener_usuario

if __name__ == "__main__":
    ok, msg = registrar("prueba", "prueba@example.com", "12345", rol="Estudiante")
    print("registrar:", ok, msg)
    print("validar:", validar("prueba", "12345"))
    print("obtener:", obtener_usuario("prueba"))