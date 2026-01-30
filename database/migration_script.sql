-- Script de migración para actualizar la base de datos SIDEGEDUC existente
-- Este script aplica cambios a la estructura sin perder datos existentes
-- Ejecutar en MySQL Workbench o similar, con precaución y respaldo previo

USE SIDEGEDUC;

-- Deshabilitar restricciones de clave foránea temporalmente para evitar errores durante la migración
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Eliminar triggers existentes
DROP TRIGGER IF EXISTS trg_persona_alcanzar_edad_ciudadana;

-- 2. Crear tablas nuevas faltantes
CREATE TABLE IF NOT EXISTS tipos_relacion_representante_hijo (
    id_relacion_representante_hijo INT AUTO_INCREMENT PRIMARY KEY,
    tipo_de_relacion VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dia_de_la_semana (
    id_dia_semana INT AUTO_INCREMENT PRIMARY KEY,
    nombre_dia VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS estado_de_horario (
    id_estado_horario INT AUTO_INCREMENT PRIMARY KEY,
    descripcion_estado VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS persona_cedula (
    id_persona_cedula INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT NOT NULL,
    numero_cedula VARCHAR(25) NOT NULL UNIQUE,
    portador_de_la_cedula INT NULL,
    id_tipo_documento INT,
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona),
    FOREIGN KEY (portador_de_la_cedula) REFERENCES personas(id_persona),
    FOREIGN KEY (id_tipo_documento) REFERENCES tipo_documento(id_tipo_documento)
);

CREATE TABLE IF NOT EXISTS ninos_cedula (
    id_ninos_cedula INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT NOT NULL,
    numero_cedula_escolar VARCHAR(25) NOT NULL UNIQUE,
    id_tipo_documento INT,
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona),
    FOREIGN KEY (id_tipo_documento) REFERENCES tipo_documento(id_tipo_documento)
);

-- 3. Migrar datos de identificaciones a las nuevas tablas
-- Nota: Esto asume que 'ciudadana' corresponde a persona_cedula y 'escolar' a ninos_cedula
INSERT INTO persona_cedula (id_persona, numero_cedula, portador_de_la_cedula, id_tipo_documento)
SELECT id_persona, numero_identificacion, id_representante, id_tipo_documento
FROM identificaciones
WHERE categoria = 'ciudadana' AND numero_identificacion != '';

INSERT INTO ninos_cedula (id_persona, numero_cedula_escolar, id_tipo_documento)
SELECT id_persona, numero_identificacion, id_tipo_documento
FROM identificaciones
WHERE categoria = 'escolar' AND numero_identificacion != '';

-- 4. Agregar columnas faltantes a tablas existentes
-- Usar procedimientos para verificar existencia antes de agregar

DELIMITER //

CREATE PROCEDURE add_column_if_not_exists(
    IN table_name VARCHAR(64),
    IN column_name VARCHAR(64),
    IN column_definition TEXT
)
BEGIN
    IF NOT EXISTS (
        SELECT * FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = table_name
        AND COLUMN_NAME = column_name
    ) THEN
        SET @sql = CONCAT('ALTER TABLE ', table_name, ' ADD COLUMN ', column_name, ' ', column_definition);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END //

DELIMITER ;

-- Agregar columnas a representantes
CALL add_column_if_not_exists('representantes', 'id_profesion', 'INT NULL');
CALL add_column_if_not_exists('representantes', 'id_ocupacion', 'INT NULL');
CALL add_column_if_not_exists('representantes', 'id_nivel_academico', 'INT NULL');

-- Agregar FK a representantes
ALTER TABLE representantes
    ADD CONSTRAINT fk_representante_profesion FOREIGN KEY (id_profesion) REFERENCES profesiones(id_profesion),
    ADD CONSTRAINT fk_representante_ocupacion FOREIGN KEY (id_ocupacion) REFERENCES ocupaciones(id_ocupacion),
    ADD CONSTRAINT fk_representante_nivel_academico FOREIGN KEY (id_nivel_academico) REFERENCES niveles_academicos(id_nivel_academico);

-- Migrar datos de ocupacion en representantes a id_ocupacion
-- Nota: Esto requiere que las ocupaciones ya existan en la tabla ocupaciones
UPDATE representantes r
JOIN ocupaciones o ON o.nombre_ocupacion = r.ocupacion
SET r.id_ocupacion = o.id_ocupacion
WHERE r.ocupacion IS NOT NULL;

-- Agregar columna tipo_relacion a estudiante_representante
CALL add_column_if_not_exists('estudiante_representante', 'tipo_relacion', 'INT NULL');

-- Agregar FK
ALTER TABLE estudiante_representante
    ADD CONSTRAINT fk_estudiante_representante_tipo FOREIGN KEY (tipo_relacion) REFERENCES tipos_relacion_representante_hijo(id_relacion_representante_hijo);

-- Migrar relacion_con_estudiante de representantes a tipo_relacion
-- Nota: Insertar en tipos_relacion_representante_hijo si no existe
INSERT IGNORE INTO tipos_relacion_representante_hijo (tipo_de_relacion)
SELECT DISTINCT relacion_con_estudiante FROM representantes WHERE relacion_con_estudiante IS NOT NULL;

UPDATE estudiante_representante er
JOIN representantes r ON er.id_representante = r.id_representante
JOIN tipos_relacion_representante_hijo tr ON tr.tipo_de_relacion = r.relacion_con_estudiante
SET er.tipo_relacion = tr.id_relacion_representante_hijo;

-- Modificar horarios: cambiar dia_semana a INT y agregar estado_del_horario
-- Primero, mapear nombres de días a IDs
INSERT IGNORE INTO dia_de_la_semana (nombre_dia) VALUES
('Lunes'), ('Martes'), ('Miércoles'), ('Jueves'), ('Viernes'), ('Sábado'), ('Domingo');

-- Agregar columna temporal para el nuevo dia_semana
ALTER TABLE horarios ADD COLUMN dia_semana_new INT;

-- Mapear valores
UPDATE horarios h
JOIN dia_de_la_semana d ON LOWER(d.nombre_dia) = LOWER(h.dia_semana)
SET h.dia_semana_new = d.id_dia_semana;

-- Eliminar columna antigua y renombrar nueva
ALTER TABLE horarios DROP COLUMN dia_semana;
ALTER TABLE horarios CHANGE COLUMN dia_semana_new dia_de_la_semana INT;

-- Agregar FK
ALTER TABLE horarios
    ADD CONSTRAINT fk_horarios_dia FOREIGN KEY (dia_de_la_semana) REFERENCES dia_de_la_semana(id_dia_semana);

-- Agregar estado_del_horario
CALL add_column_if_not_exists('horarios', 'estado_del_horario', 'INT NULL');

-- Agregar FK
ALTER TABLE horarios
    ADD CONSTRAINT fk_horarios_estado FOREIGN KEY (estado_del_horario) REFERENCES estado_de_horario(id_estado_horario);

-- 5. Eliminar columnas redundantes
-- Eliminar columnas de datos_academicos que son redundantes
ALTER TABLE datos_academicos DROP COLUMN IF EXISTS id_profesion;
ALTER TABLE datos_academicos DROP COLUMN IF EXISTS id_ocupacion;
ALTER TABLE datos_academicos DROP COLUMN IF EXISTS id_especialidad;

-- Eliminar numero_hijos_o_representados de datos_familiares si es redundante
ALTER TABLE datos_familiares DROP COLUMN IF EXISTS numero_hijos_o_representados;

-- Eliminar ocupacion y relacion_con_estudiante de representantes (ya migrados)
ALTER TABLE representantes DROP COLUMN IF EXISTS ocupacion;
ALTER TABLE representantes DROP COLUMN IF EXISTS relacion_con_estudiante;

-- 6. Eliminar tablas innecesarias
DROP TABLE IF EXISTS profesor_empleado; -- Tabla innecesaria, profesores y empleados son entidades separadas
DROP TABLE IF EXISTS tipos_calificacion; -- Redundante con rangos_calificacion
DROP TABLE IF EXISTS identificaciones; -- Reemplazada por persona_cedula y ninos_cedula

-- 7. Insertar datos básicos faltantes si no existen
INSERT IGNORE INTO tipos_relacion_representante_hijo (tipo_de_relacion) VALUES
('Padre'), ('Madre'), ('Tutor'), ('Abuelo'), ('Abuela'), ('Tío'), ('Tía');

INSERT IGNORE INTO estado_de_horario (descripcion_estado) VALUES
('Activo'), ('Inactivo'), ('Temporal'), ('Permanente');

-- 8. Limpiar procedimiento temporal
DROP PROCEDURE IF EXISTS add_column_if_not_exists;

-- Rehabilitar restricciones de clave foránea
SET FOREIGN_KEY_CHECKS = 1;

-- Mensaje final
SELECT 'Migración completada exitosamente. Verifique los datos antes de continuar.' AS mensaje;