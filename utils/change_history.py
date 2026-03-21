import json
from datetime import datetime
from sqlalchemy import text
from database.models import db


def ensure_change_history_table():
    db.session.execute(text('''
        CREATE TABLE IF NOT EXISTS change_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            action_type TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id INTEGER,
            description TEXT,
            payload_json TEXT,
            undo_supported INTEGER DEFAULT 0,
            undone INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    '''))


def prune_old_changes(days=7):
    db.session.execute(
        text("DELETE FROM change_history WHERE datetime(created_at) < datetime('now', :days_expr)"),
        {'days_expr': f'-{int(days)} days'}
    )
    db.session.commit()


def log_change(user_id, username, action_type, entity_type, entity_id=None, description='', payload=None, undo_supported=False):
    try:
        ensure_change_history_table()
        payload_json = json.dumps(payload or {}, ensure_ascii=False)
        db.session.execute(text('''
            INSERT INTO change_history (
                user_id, username, action_type, entity_type, entity_id,
                description, payload_json, undo_supported, undone, created_at
            ) VALUES (
                :user_id, :username, :action_type, :entity_type, :entity_id,
                :description, :payload_json, :undo_supported, 0, :created_at
            )
        '''), {
            'user_id': user_id,
            'username': username or 'Usuario',
            'action_type': action_type,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'description': description,
            'payload_json': payload_json,
            'undo_supported': 1 if undo_supported else 0,
            'created_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception:
        # El historial nunca debe romper la operacion principal.
        pass


def list_changes(limit=300):
    rows = db.session.execute(text('''
        SELECT id, user_id, username, action_type, entity_type, entity_id, description,
               payload_json, undo_supported, undone, created_at
        FROM change_history
        ORDER BY id DESC
        LIMIT :limit
    '''), {'limit': int(limit)}).fetchall()
    out = []
    for r in rows:
        payload = {}
        try:
            payload = json.loads(r[7] or '{}')
        except Exception:
            payload = {}
        out.append({
            'id': r[0],
            'user_id': r[1],
            'username': r[2],
            'action_type': r[3],
            'entity_type': r[4],
            'entity_id': r[5],
            'description': r[6],
            'payload': payload,
            'undo_supported': bool(r[8]),
            'undone': bool(r[9]),
            'created_at': r[10],
        })
    return out


def undo_change(change_id):
    ensure_change_history_table()
    row = db.session.execute(text('''
        SELECT id, action_type, entity_type, entity_id, payload_json, undo_supported, undone
        FROM change_history
        WHERE id = :id
    '''), {'id': int(change_id)}).fetchone()
    if not row:
        return False, 'Cambio no encontrado.'
    if not row[5]:
        return False, 'Este cambio no permite deshacer.'
    if row[6]:
        return False, 'Este cambio ya fue deshecho.'

    try:
        payload = json.loads(row[4] or '{}')
    except Exception:
        payload = {}

    action = row[1]
    entity = row[2]
    entity_id = row[3]

    try:
        if action == 'create' and entity == 'materia' and entity_id:
            db.session.execute(text('DELETE FROM materias WHERE id_materia = :id'), {'id': entity_id})
        elif action == 'create' and entity == 'seccion' and entity_id:
            db.session.execute(text('DELETE FROM secciones WHERE id_seccion = :id'), {'id': entity_id})
        elif action == 'create' and entity == 'plantel' and entity_id:
            db.session.execute(text('DELETE FROM planteles WHERE id_plantel = :id'), {'id': entity_id})
        elif action == 'link' and entity == 'estudiante_seccion':
            db.session.execute(text('DELETE FROM estudiante_seccion WHERE id_estudiante = :est AND id_seccion = :sec'),
                               {'est': payload.get('id_estudiante'), 'sec': payload.get('id_seccion')})
        elif action == 'link' and entity == 'profesor_seccion':
            db.session.execute(text('DELETE FROM profesor_seccion WHERE id_profesor = :prof AND id_seccion = :sec'),
                               {'prof': payload.get('id_profesor'), 'sec': payload.get('id_seccion')})
        elif action == 'link' and entity == 'materia_seccion':
            db.session.execute(text('DELETE FROM materias_seccion WHERE id_materia = :mid AND id_seccion = :sid'),
                               {'mid': payload.get('id_materia'), 'sid': payload.get('id_seccion')})
        else:
            return False, 'Tipo de cambio no soportado para deshacer.'

        db.session.execute(text('UPDATE change_history SET undone = 1 WHERE id = :id'), {'id': int(change_id)})
        db.session.commit()
        return True, 'Cambio deshecho correctamente.'
    except Exception as e:
        db.session.rollback()
        return False, f'No se pudo deshacer: {e}'
