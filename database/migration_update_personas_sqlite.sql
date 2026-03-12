-- Actualización urgente tabla personas para SQLite
ALTER TABLE personas ADD COLUMN id_tipo_persona INTEGER;
ALTER TABLE personas ADD COLUMN id_tipo_documento INTEGER;
ALTER TABLE personas ADD COLUMN numero_cedula TEXT;
ALTER TABLE personas ADD COLUMN id_ocupacion INTEGER;
ALTER TABLE personas ADD COLUMN id_profesion INTEGER;
ALTER TABLE personas ADD COLUMN num_hijos INTEGER;
ALTER TABLE personas ADD COLUMN id_relacion_familiar INTEGER;
-- SQLite no soporta ADD FOREIGN KEY directamente, pero los modelos ya lo gestionan en SQLAlchemy
-- Si alguna columna ya existe, omitir ese ALTER
