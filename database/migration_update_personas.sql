-- Actualización urgente tabla personas
ALTER TABLE personas
    ADD COLUMN id_tipo_persona INT NOT NULL,
    ADD COLUMN id_tipo_documento INT NULL,
    ADD COLUMN numero_cedula VARCHAR(20) NULL,
    ADD COLUMN id_ocupacion INT NULL,
    ADD COLUMN id_profesion INT NULL,
    ADD COLUMN num_hijos INT NULL,
    ADD COLUMN id_relacion_familiar INT NULL,
    ADD FOREIGN KEY (id_tipo_persona) REFERENCES tipo_persona(id_tipo_persona),
    ADD FOREIGN KEY (id_tipo_documento) REFERENCES tipo_documento(id_tipo_documento),
    ADD FOREIGN KEY (id_ocupacion) REFERENCES ocupaciones(id),
    ADD FOREIGN KEY (id_profesion) REFERENCES profesiones(id),
    ADD FOREIGN KEY (id_relacion_familiar) REFERENCES relaciones_familiares(id);

-- Si alguna columna ya existe, omitir ese ALTER
-- Ejecutar este script en la base de datos para aplicar los cambios
