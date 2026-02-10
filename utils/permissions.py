# este script es para comprobar roles y obtener contexto de usuario
# las funciones aqui son usadas en las vistas para verificar permisos.
#aun no esta terminado se iso con la intencion de probar como dar permisos privilegios a los usuarios
from database.models import Usuarios, Roles, StatusUser


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
    role_name = None
    role_desc = None
    status = None
    is_creator = False

    if 'user_id' in session:
        try:
            uid = session.get('user_id')
            uobj = Usuarios.query.filter_by(id_user=uid).first()
            if uobj:
                user = uobj.nombre
                current_user_id = uobj.id_user
                role = Roles.query.filter_by(id_rol=uobj.id_rol).first()
                role_name = (role.nombre_rol or '') if role else None
                # Obtener estado de usuario (activo, suspendido, inactivo, etc.)
                try:
                    st = StatusUser.query.filter_by(id_status_user=uobj.id_status_user).first()
                    status = (st.estado or '') if st else None
                except Exception:
                    status = None

                # Concede privilegios a desarrolladores, administradores o personal empleado
                rn = (role_name or '').lower()
                # El rol especial 'Creador' tiene todos los privilegios
                if role_name and role_name.lower() == 'creador':
                    developer_priv = True
                    is_creator = True
                if 'desarroll' in rn or 'administr' in rn or 'empleado' in rn:
                    developer_priv = True

                # Descripción breve según rol (para mostrar en el resumen)
                if role_name:
                    rn_l = rn
                    if 'desarroll' in rn_l:
                        role_desc = 'Acceso a herramientas de desarrollo y gestión del sistema.'
                    elif 'administr' in rn_l:
                        role_desc = 'Puede administrar usuarios y configuraciones del sistema.'
                    elif 'empleado' in rn_l:
                        role_desc = 'Acceso a funciones internas para personal administrativo.'
                    else:
                        role_desc = 'Acceso estándar según permisos asignados.'
        except Exception:
            # En caso de error con la BD, devolvemos valores por defecto para seguridad
            user = None
            developer_priv = False
            current_user_id = None

    return {
        'user': user,
        'developer_priv': developer_priv,
        'current_user_id': current_user_id,
        'role_name': role_name,
        'role_desc': role_desc,
        'status': status,
        'is_creator': is_creator
    }


def user_has_admin_privileges(session):
    """
    Versión rápida para comprobaciones booleanas esto es porque se necesita saber si el usuario puede acceder.
    """
    ctx = get_user_context(session)
    return bool(ctx['developer_priv'])
