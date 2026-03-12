-- Script SQLite para actualizar la tabla personas
PRAGMA foreign_keys=off;

ALTER TABLE personas ADD COLUMN id_tipo_persona INTEGER;
ALTER TABLE personas ADD COLUMN id_tipo_documento INTEGER;
ALTER TABLE personas ADD COLUMN numero_cedula TEXT;
ALTER TABLE personas ADD COLUMN id_ocupacion INTEGER;
ALTER TABLE personas ADD COLUMN id_profesion INTEGER;
ALTER TABLE personas ADD COLUMN num_hijos INTEGER;
ALTER TABLE personas ADD COLUMN id_relacion_familiar INTEGER;

PRAGMA foreign_keys=on;

-- NOTA: SQLite no permite agregar FKs con ALTER TABLE, pero los modelos SQLAlchemy ya gestionan las relaciones.
-- Si alguna columna ya existe, omitir ese ALTER.
-- Ejecuta este script con el CLI de SQLite o desde Python.
