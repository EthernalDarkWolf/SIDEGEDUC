-- Tabla para relaciones de parentesco (familiares)
CREATE TABLE IF NOT EXISTS parentescos (
    id_parentesco INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_parentesco VARCHAR(50) UNIQUE NOT NULL
);

-- Ejemplo de inserciones iniciales
INSERT INTO parentescos (nombre_parentesco) VALUES
('Padre'),
('Madre'),
('Hermano/a'),
('Abuelo/a'),
('Tío/a'),
('Primo/a'),
('Otro');
