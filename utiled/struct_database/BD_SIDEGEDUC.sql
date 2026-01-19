
CREATE DATABASE SIDEGEDUC;
USE SIDEGEDUC;

-- Tablas de referencia básicas (sistema) se dejo esta tabla solo para roles del sistema no cargos :v
CREATE TABLE roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE status_user (
    id_status_user INT AUTO_INCREMENT PRIMARY KEY,
    estado VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE tipo_documento (
    id_tipo_documento INT AUTO_INCREMENT PRIMARY KEY,
    nombre_tipo_documento VARCHAR(50) NOT NULL UNIQUE -- pasaporte, pasaporte extranjero, cedula nacional, cedula extranjera, rif, cedula escolar etc.(en tabla persona debe tener uno de estos)
);

CREATE TABLE sexo (
    id_sexo INT AUTO_INCREMENT PRIMARY KEY,
    letra_sexo CHAR(1) NOT NULL UNIQUE -- M o F
);

CREATE TABLE nacionalidad (
    id_pais INT AUTO_INCREMENT PRIMARY KEY,
    nombre_pais VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE ciudades (
    id_ciudad INT AUTO_INCREMENT PRIMARY KEY,
    nombre_ciudad VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE direcciones (
    id_direccion INT AUTO_INCREMENT PRIMARY KEY,
    direccion TEXT NOT NULL,
    id_ciudad INT,
    id_pais INT,
    FOREIGN KEY (id_ciudad) REFERENCES ciudades(id_ciudad),
    FOREIGN KEY (id_pais) REFERENCES nacionalidad(id_pais)
);

-- esta tabla es para los contactos de las personas dentro del planten esta en muchos a muchos (esta tabla es ajena al contacto que ay en tabla usuarios)
CREATE TABLE contactos (
    id_contacto INT AUTO_INCREMENT PRIMARY KEY,
    telefono VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE
);

-- estados civil como casado o soltero
CREATE TABLE estados_civiles (
    id_estado_civil INT AUTO_INCREMENT PRIMARY KEY,
    descripcion_estado_civil VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE religiones (
    id_religion INT AUTO_INCREMENT PRIMARY KEY,
    nombre_religion VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE niveles_academicos (
    id_nivel_academico INT AUTO_INCREMENT PRIMARY KEY,
    nombre_nivel_academico VARCHAR(100) NOT NULL UNIQUE
);

-- orientaciones o especialidades de los profesores/representantes segun sea el caso
CREATE TABLE especialidades (
    id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
    nombre_especialidad VARCHAR(100) NOT NULL UNIQUE
);

-- para referenciar las profesiones de los representantes
CREATE TABLE profesiones (
    id_profesion INT AUTO_INCREMENT PRIMARY KEY,
    nombre_profesion VARCHAR(100) NOT NULL UNIQUE
);
-- para referenciar las ocupaciones de los representantes
CREATE TABLE ocupaciones (
    id_ocupacion INT AUTO_INCREMENT PRIMARY KEY,
    nombre_ocupacion VARCHAR(100) NOT NULL UNIQUE
);

-- Niveles educativos 
CREATE TABLE niveles (
    id_nivel INT AUTO_INCREMENT PRIMARY KEY,
    nombre_nivel VARCHAR(50) NOT NULL UNIQUE  -- Maternal, Inicial, Preescolar, Primaria
);

-- Grados (para primaria y extensible)
CREATE TABLE grados (
    id_grado INT AUTO_INCREMENT PRIMARY KEY,
    numero_grado TINYINT NOT NULL UNIQUE -- son para los numeros de 1er, 2do, 3er, etc
);
create table letra_seccion(
    id_letra_seccion INT AUTO_INCREMENT PRIMARY KEY,
    letra CHAR(1) NOT NULL UNIQUE -- puede ser A o B o si ay un cambio aqui se realiza
);
-- E/R para la contruccion de la seccion :3
CREATE TABLE secciones (
    id_seccion INT AUTO_INCREMENT PRIMARY KEY,
    id_letra_seccion INT, -- letra de la seccion
    id_grado INT NULL, -- 1ero, 2do, 3er, etc (puede excluirse dependiendo del nivel academico)
    id_nivel INT, -- es para identificar si la seccion pertenece a nivel primaria, preescolar, o maternal
    FOREIGN KEY (id_grado) REFERENCES grados(id_grado),
    FOREIGN KEY (id_letra_seccion) REFERENCES letra_seccion(id_letra_seccion),
    FOREIGN KEY (id_nivel) REFERENCES niveles(id_nivel)
);

-- E/R para identificar que alumnos pertenecen a una seccion (es muchos a muchos y funciona para realizar cambios de alumno con su seccion):
-- Relaciones muchos-a-muchos entre personas y secciones (se crearán más abajo
-- después de definir `estudiantes` y `profesores` para evitar referencias a tablas
-- aún no creadas).

-- Materias
CREATE TABLE materias (
    id_materia INT AUTO_INCREMENT PRIMARY KEY,
    nombre_materia VARCHAR(100) NOT NULL UNIQUE
);

-- E/r  materias con seccion: es para identificar las materias que dictara una seccion 
CREATE TABLE materias_seccion (
    id_materia_nivel INT AUTO_INCREMENT PRIMARY KEY,
    id_materia INT,
    id_seccion INT,
    FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion),
    FOREIGN KEY (id_materia) REFERENCES materias(id_materia)
);

-- Cargos para empleados (dentro del plantel)
CREATE TABLE cargos (
    id_cargo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cargo VARCHAR(100) NOT NULL UNIQUE -- Director, Secretaria, Portero, etc.
);

-- Planteles / centros educativos (campos solicitados en la planilla)
CREATE TABLE planteles (
    id_plantel INT AUTO_INCREMENT PRIMARY KEY,
    ccid_estado VARCHAR(100) NULL,
    estado VARCHAR(100) NULL,
    municipio VARCHAR(100) NULL,
    parroquia VARCHAR(100) NULL,
    codigo_dependencia VARCHAR(100) NULL,
    codigo_estadistico VARCHAR(100) NULL,
    codigo_plantel VARCHAR(100) NULL,
    nombre_plantel_nomina VARCHAR(200) NULL,
    id_nivel INT NULL,
    modalidad VARCHAR(100) NULL,
    ubicacion_geografica ENUM('Rural','Urbana') NULL,
    turnos VARCHAR(200) NULL,
    codigo_pa VARCHAR(100) NOT NULL UNIQUE,
    id_cargo INT NULL,
    FOREIGN KEY (id_nivel) REFERENCES niveles(id_nivel),
    FOREIGN KEY (id_cargo) REFERENCES cargos(id_cargo)
);

-- Tipos de calificación 
CREATE TABLE tipos_calificacion (
    id_tipo_calificacion INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL UNIQUE  -- puede ser tipo Numerica, Letra
);

create table fuente_de_ingresos(
    id_fuente_ingresos INT AUTO_INCREMENT PRIMARY KEY,
    nombre_fuente VARCHAR(100) NOT NULL UNIQUE
);
-- Tabla base: Personas ( basicamente para todos: estudiantes, profesores, empleados, representantes)
CREATE TABLE personas (
    id_persona INT AUTO_INCREMENT PRIMARY KEY,
    primer_nombre VARCHAR(50) NOT NULL,
    segundo_nombre VARCHAR(50),
    primer_apellido VARCHAR(50) NOT NULL,
    segundo_apellido VARCHAR(50),
    fecha_nacimiento DATE,
    id_sexo INT,
    FOREIGN KEY (id_sexo) REFERENCES sexo(id_sexo)
);

-- Usuarios (para acceso al sistema)
CREATE TABLE usuarios (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    id_rol INT,
    id_status_user INT,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol),
    FOREIGN KEY (id_status_user) REFERENCES status_user(id_status_user)
);

-- e/r para relacionar usuarios del sistema con personas (muchos a muchos)
create table usuario_persona(
    id_usuario_persona INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT,
    id_persona INT,
    FOREIGN KEY (id_user) REFERENCES usuarios(id_user),
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona)
);
-- Estudiantes (extensión de personas)
CREATE TABLE estudiantes (
    id_estudiante INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT,
    fecha_inscripcion DATE NOT NULL,
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona)
);

-- Profesores (extensión de personas)
CREATE TABLE profesores (
    id_profesor INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT,
    id_especialidad INT,
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona),
    FOREIGN KEY (id_especialidad) REFERENCES especialidades(id_especialidad)
);

-- Relaciones muchos-a-muchos entre estudiantes/profesores y secciones
CREATE TABLE estudiante_seccion (
    id_estudiante_seccion INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT NOT NULL,
    id_seccion INT NOT NULL,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante),
    FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion)
);

CREATE TABLE profesor_seccion (
    id_profesor_seccion INT AUTO_INCREMENT PRIMARY KEY,
    id_profesor INT NOT NULL,
    id_seccion INT NOT NULL,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor),
    FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion)
);

-- Empleados (extensión de personas, con cargos)
CREATE TABLE empleados (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT,
    id_cargo INT,
    fecha_contratacion DATE,
    salario DECIMAL(10,2),
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona),
    FOREIGN KEY (id_cargo) REFERENCES cargos(id_cargo)
);

-- Representantes (padres/tutores de estudiantes)
CREATE TABLE representantes (
    id_representante INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT,
    ocupacion VARCHAR(100),
    relacion_con_estudiante VARCHAR(50),  -- Padre, Madre, Tutor, etc.
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona)
);

-- Relación estudiantes-representantes (muchos a muchos)
CREATE TABLE estudiante_representante (
    id_estudiante_representante INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT,
    id_representante INT,
    es_representante_principal BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante),
    FOREIGN KEY (id_representante) REFERENCES representantes(id_representante)
);

-- Historial de estudiantes (cambios de nivel/sección)

create table motivos_cambio_seccion(
    id_motivo_cambio INT AUTO_INCREMENT PRIMARY KEY,
    descripcion_motivo VARCHAR(100) NOT NULL UNIQUE
);
CREATE TABLE historial_estudiantes (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT,
    id_seccion_anterior INT NULL,
    id_seccion_nuevo INT,
    fecha_cambio DATE NOT NULL,
    id_motivo_del_cambio INT,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante),
    FOREIGN KEY (id_seccion_anterior) REFERENCES secciones(id_seccion),
    FOREIGN KEY (id_seccion_nuevo) REFERENCES secciones(id_seccion),
    FOREIGN KEY (id_motivo_del_cambio) REFERENCES motivos_cambio_seccion(id_motivo_cambio)
);

-- Datos adicionales por persona  profesor, representante, empleado estudiante no tiene logica aqui
CREATE TABLE datos_academicos (
    id_datos_academicos INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT,
    id_nivel_academico INT,
    institucion VARCHAR(100) NULL,
    anio_graduacion YEAR,
    id_profesion INT,
    id_ocupacion INT,
    id_especialidad INT,
    sabe_leer BOOLEAN,
    sabe_escribir BOOLEAN,
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona),
    FOREIGN KEY (id_nivel_academico) REFERENCES niveles_academicos(id_nivel_academico),
    FOREIGN KEY (id_profesion) REFERENCES profesiones(id_profesion),
    FOREIGN KEY (id_ocupacion) REFERENCES ocupaciones(id_ocupacion),
    FOREIGN KEY (id_especialidad) REFERENCES especialidades(id_especialidad)
);

CREATE TABLE datos_economicos (
    id_datos_economicos INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT,
    ingresos_mensuales DECIMAL(10,2),
    id_fuente_ingresos INT,
    FOREIGN KEY (id_fuente_ingresos) REFERENCES fuente_de_ingresos(id_fuente_ingresos),
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona)
);

CREATE TABLE datos_familiares (
    id_datos_familiares INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT,
    id_estado_civil INT,
    id_religion INT,
    numero_hijos_o_representados VARCHAR(50),
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona),
    FOREIGN KEY (id_estado_civil) REFERENCES estados_civiles(id_estado_civil),
    FOREIGN KEY (id_religion) REFERENCES religiones(id_religion)
);

-- Relación personas con contactos (muchos a muchos)
CREATE TABLE persona_contacto (
    id_persona_contacto INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT,
    id_contacto INT,
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona),
    FOREIGN KEY (id_contacto) REFERENCES contactos(id_contacto)
);

-- Horarios
CREATE TABLE horarios (
    id_horario INT AUTO_INCREMENT PRIMARY KEY,
    id_seccion INT,
    id_materia INT,
    dia_semana VARCHAR(20) NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion),
    FOREIGN KEY (id_materia) REFERENCES materias(id_materia)
);

-- Calificaciones

CREATE TABLE rangos_calificacion (
    id_rango_calificacion INT AUTO_INCREMENT PRIMARY KEY,
    rango_letra CHAR(1) NOT NULL UNIQUE -- A, B, C, D, E, F
);
CREATE TABLE calificaciones (
    id_calificacion INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT,
    id_materia_presentada INT NULL,
    calificacion_en_materia_presentada DECIMAL(5,2) NULL, -- este campo se usara en backend para calcular el ramgo de calificacion
    rango_letra INT, -- este es basicamente el campo que dice si pasaste con  A, B, C, D, E, F
    fecha_calificacion DATE,
    observaciones text null,
    FOREIGN KEY (rango_letra) REFERENCES rangos_calificacion(id_rango_calificacion),
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante),
    FOREIGN KEY (id_materia_presentada) REFERENCES materias(id_materia)
);

-- Asistencia
CREATE TABLE asistencia (
    id_asistencia INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT,
    fecha DATE NOT NULL,
    estado_asistencia VARCHAR(20) NOT NULL,
    id_seccion INT,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante),
    FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion)
);

-- Matrículas (inscripciones anuales)
CREATE TABLE matriculas (
    id_matricula INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT,
    anio_academico YEAR NOT NULL,
    fecha_matricula DATE NOT NULL,
    monto_matricula DECIMAL(10,2),
    pago_realizado BOOLEAN DEFAULT FALSE,
    estado_matricula VARCHAR(20) NOT NULL,  -- Activa, Inactiva
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante)
);

-- Evaluaciones adicionales (exámenes, proyectos etc.)
CREATE TABLE evaluaciones (
    id_evaluacion INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT,
    materia_adicional INT, -- esta aqui es para identificar la materia a la que pertenece la evaluacion adicional
    nombre_evaluacion VARCHAR(100) NOT NULL,
    fecha_evaluacion DATE,
    tipo_evaluacion VARCHAR(50),  -- Examen, Proyecto, Tarea
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante),
    FOREIGN KEY (materia_adicional) REFERENCES materias(id_materia)
);

-- Certificaciones de profesores
CREATE TABLE certificaciones_profesor (
    id_certificacion INT AUTO_INCREMENT PRIMARY KEY,
    id_profesor INT,
    nombre_certificacion VARCHAR(100) NOT NULL,
    institucion VARCHAR(100),
    fecha_obtencion DATE,
    fecha_vencimiento DATE NULL,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor)
);

-- Experiencia laboral de profesores
CREATE TABLE experiencia_profesor (
    id_experiencia INT AUTO_INCREMENT PRIMARY KEY,
    id_profesor INT,
    institucion VARCHAR(100) NOT NULL,
    cargo VARCHAR(100) NOT NULL,
    fecha_inicio DATE,
    fecha_fin DATE NULL,
    descripcion TEXT,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor)
);

-- Evaluaciones de desempeño de profesores
CREATE TABLE evaluaciones_profesor (
    id_evaluacion_profesor INT AUTO_INCREMENT PRIMARY KEY,
    id_profesor INT,
    fecha_evaluacion DATE NOT NULL,
    evaluador VARCHAR(100),  -- Nombre del evaluador (director, administador etc.)
    puntuacion DECIMAL(2,1), -- Escala 1-10  
    comentarios TEXT,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor)
);

-- Tutorías: Profesores como tutores de estudiantes en casos de un niño con dificultades o condiciones especiales
CREATE TABLE tutorias (
    id_tutoria INT AUTO_INCREMENT PRIMARY KEY,
    id_profesor INT,
    id_estudiante INT,
    tipo_tutoria VARCHAR(50),  -- Académica, Disciplinaria, etc.
    fecha_inicio DATE,
    fecha_fin DATE NULL,
    descripcion TEXT,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor),
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante)
);

-- Cursos/materias o capacitaciones que imparten profesores (mejor dicho en que se especializan)
CREATE TABLE capacitaciones_profesor (
    id_capacitacion INT AUTO_INCREMENT PRIMARY KEY,
    id_profesor INT,
    nombre_capacitacion VARCHAR(100) NOT NULL,
    descripcion TEXT,
    fecha DATE,
    duracion_horas INT,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor)
);

-- Relación profesores con empleados (si un profesor también es empleado administrativo)
CREATE TABLE profesor_empleado (
    id_profesor_empleado INT AUTO_INCREMENT PRIMARY KEY,
    id_profesor INT,
    id_empleado INT,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor),
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

-- Añadir campos solicitados por la planilla
ALTER TABLE personas
    ADD COLUMN tipo_persona VARCHAR(50) NULL; -- indica si es docente, estudiante, representante, empleado, etc.

ALTER TABLE profesores
    ADD COLUMN tipo_docente VARCHAR(100) NULL,
    ADD COLUMN id_plantel INT NULL,
    ADD CONSTRAINT fk_profesor_plantel FOREIGN KEY (id_plantel) REFERENCES planteles(id_plantel);

ALTER TABLE empleados
    ADD COLUMN id_plantel INT NULL,
    ADD CONSTRAINT fk_empleado_plantel FOREIGN KEY (id_plantel) REFERENCES planteles(id_plantel);

-- Tabla para identificar documentos de identidad (cedula ciudadana o escolar)
CREATE TABLE identificaciones (
    id_identificacion INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT NOT NULL,
    id_tipo_documento INT NULL, -- referencia a tipo_documento (cedula nacional, cedula escolar, etc.)
    categoria ENUM('ciudadana','escolar') NOT NULL COMMENT 'ciudadana: cedula nacional; escolar: cedula escolar asociada a representante',
    numero_identificacion VARCHAR(100) NOT NULL,
    fecha_emision DATE NULL,
    vigente BOOLEAN DEFAULT TRUE,
    id_representante INT NULL, -- referido cuando categoria='escolar'
    informacion_adicional TEXT,
    UNIQUE KEY uq_persona_categoria (id_persona, categoria),
    UNIQUE KEY uq_numero_identificacion (numero_identificacion),
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona),
    FOREIGN KEY (id_tipo_documento) REFERENCES tipo_documento(id_tipo_documento),
    FOREIGN KEY (id_representante) REFERENCES representantes(id_representante),
    CHECK (categoria <> 'escolar' OR id_representante IS NOT NULL)
);

-- Trigger: cuando la persona alcanza la edad configurada (ej. 18 años), se crea
-- un registro de tipo 'ciudadana' si no existe aún. Ajustar la constante `EDAD_CIUDADANA`
-- según la normativa local.
DELIMITER $$
CREATE TRIGGER trg_persona_alcanzar_edad_ciudadana
AFTER UPDATE ON personas
FOR EACH ROW
BEGIN
    DECLARE EDAD_CIUDADANA INT DEFAULT 9; -- ajustar según necesidad
    IF (OLD.fecha_nacimiento IS NOT NULL) THEN
        IF (TIMESTAMPDIFF(YEAR, NEW.fecha_nacimiento, CURDATE()) >= EDAD_CIUDADANA)
           AND (SELECT COUNT(*) FROM identificaciones WHERE id_persona = NEW.id_persona AND categoria = 'ciudadana') = 0 THEN
            INSERT INTO identificaciones (id_persona, categoria, numero_identificacion, fecha_emision, vigente, informacion_adicional)
            VALUES (NEW.id_persona, 'ciudadana', '', NULL, TRUE, 'Generado automáticamente: pendiente número de cédula');
        END IF;
    END IF;
END$$
DELIMITER ;