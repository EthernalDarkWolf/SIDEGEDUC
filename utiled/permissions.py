# este script es para comprobar roles y obtener contexto de usuario
# las funciones aqui son usadas en las vistas para verificar permisos.
#aun no esta terminado se iso con la intencion de probar como dar permisos privilegios a los usuarios
from database.models import Usuarios, Roles


def get_user_context(session): #esto es la funcion que se reutiliza  para obtener el contexto del usuario desde la sesión
    """
    Devuelve un diccionario con la información mínima que usan las vistas:
    - user: nombre de usuario o None
    - developer_priv: True si el usuario tiene privilegios de desarrollador/administrativo
    - current_user_id: id numérico del usuario (si está logueado)

    Esta función centraliza la lógica de verificación de roles para evitar
    repetir el mismo código en múltiples rutas.
    """
    user = None
    developer_priv = False
    current_user_id = None

    if 'user_id' in session:
        try:
            uid = session.get('user_id')
            uobj = Usuarios.query.filter_by(id_user=uid).first()
            if uobj:
                user = uobj.nombre
                current_user_id = uobj.id_user
                role = Roles.query.filter_by(id_rol=uobj.id_rol).first()
                role_name = (role.nombre_rol or '').lower() if role else ''
                # Concede privilegios a desarrolladores, administradores o personal empleado
                if 'desarroll' in role_name or 'administr' in role_name or 'empleado' in role_name:
                    developer_priv = True #los privilegios de desarrollador son verdaderos
        except Exception:
            # En caso de error con la BD, devolvemos valores por defecto para seguridad
            user = None
            developer_priv = False
            current_user_id = None

    return {
        'user': user,
        'developer_priv': developer_priv,
        'current_user_id': current_user_id
    }


def user_has_admin_privileges(session):
    """
    Versión rápida para comprobaciones booleanas esto es porque se necesita saber si el usuario puede acceder.
    """
    ctx = get_user_context(session)
    return bool(ctx['developer_priv'])
