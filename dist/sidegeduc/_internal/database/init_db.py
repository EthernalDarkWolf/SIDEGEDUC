"""Inicia/actualiza la base de datos de SIDEGEDUC.

Este script crea las tablas que definen los modelos de SQLAlchemy y
asegura que existan datos de referencia mínimos para poder usar el sistema.

Uso:
    python -m database.init_db

Opciones (por ahora no hay flags, pero puede extenderse en el futuro).
"""

from __future__ import annotations

from app import app
from database.models import (
    db,
    Sexo,
    TipoDocumento,
    TipoPersona,
    Roles,
    StatusUser,
    Niveles,
    Grados,
    LetraSeccion,
    RelacionFamiliar,
    Parentesco,
)


def _ensure_lookup(model, unique_field: str, values: list[str]) -> None:
    """Inserta registros de soporte si no existen (no es destructivo)."""
    existing = {getattr(r, unique_field) for r in db.session.query(model).all()}
    for v in values:
        if v not in existing:
            obj = model(**{unique_field: v})
            db.session.add(obj)
    db.session.commit()


def init_db() -> None:
    """Crea las tablas y datos iniciales necesarios"""
    with app.app_context():
        # Crear tablas definidas en los modelos (idempotente)
        db.create_all()

        # Datos base
        _ensure_lookup(Sexo, 'letra_sexo', ['M', 'F', 'O'])
        _ensure_lookup(TipoDocumento, 'nombre_tipo_documento', ['Cédula', 'Pasaporte', 'Otro'])
        _ensure_lookup(TipoPersona, 'nombre_tipo_persona', ['Estudiante', 'Profesor', 'Representante', 'Empleado'])
        _ensure_lookup(Roles, 'nombre_rol', ['Creador', 'Administrador', 'Usuario'])
        _ensure_lookup(StatusUser, 'estado', ['Activo', 'Inactivo', 'Bloqueado'])
        _ensure_lookup(Niveles, 'nombre_nivel', ['Preescolar', 'Primaria', 'Secundaria', 'Media'])
        _ensure_lookup(Grados, 'numero_grado', [1, 2, 3, 4, 5, 6, 7])
        _ensure_lookup(LetraSeccion, 'letra', ['A', 'B', 'C', 'D', 'E'])
        _ensure_lookup(RelacionFamiliar, 'nombre', ['Padre', 'Madre', 'Hermano', 'Tío', 'Tía', 'Otro'])
        _ensure_lookup(Parentesco, 'nombre_parentesco', ['Padre', 'Madre', 'Hermano', 'Tío', 'Tía', 'Tutor'])

        print('Base de datos inicializada correctamente.')


if __name__ == '__main__':
    init_db()
