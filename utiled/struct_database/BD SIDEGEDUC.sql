
CREATE DATABASE BD_SIDEGEDUC;
USE BD_SIDEGEDUC;

-- Tablas de referencia básicas
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
    nombre_tipo_documento VARCHAR(50) NOT NULL UNIQUE --pasaporte, pasaporte extranjero, cedula nacional, cedula extranjera, rif, cedula escolar etc.(en tabla persona debe tener uno de estos)
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

CREATE TABLE contactos (
    id_contacto INT AUTO_INCREMENT PRIMARY KEY,
    telefono VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE
);

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

CREATE TABLE especialidades (
    id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
    nombre_especialidad VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE profesiones (
    id_profesion INT AUTO_INCREMENT PRIMARY KEY,
    nombre_profesion VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE ocupaciones (
    id_ocupacion INT AUTO_INCREMENT PRIMARY KEY,
    nombre_ocupacion VARCHAR(100) NOT NULL UNIQUE
);

-- Niveles educativos 
CREATE TABLE niveles (
    id_nivel INT AUTO_INCREMENT PRIMARY KEY,
    nombre_nivel VARCHAR(50) NOT NULL UNIQUE,  -- Maternal, Inicial, Preescolar, Primaria
    descripcion TEXT
);

-- Grados (para primaria y extensible)
CREATE TABLE grados (
    id_grado INT AUTO_INCREMENT PRIMARY KEY,
    numero_grado TINYINT NOT NULL UNIQUE,  -- 1-6
    id_nivel INT,
    FOREIGN KEY (id_nivel) REFERENCES niveles(id_nivel)
);

-- Secciones (A/B por grado/nivel)
CREATE TABLE secciones (
    id_seccion INT AUTO_INCREMENT PRIMARY KEY,
    letra_seccion CHAR(1) NOT NULL,  -- A o B
    id_grado INT NULL,
    id_nivel INT,
    FOREIGN KEY (id_grado) REFERENCES grados(id_grado),
    FOREIGN KEY (id_nivel) REFERENCES niveles(id_nivel),
    UNIQUE (letra_seccion, id_grado, id_nivel)
);

-- Materias
CREATE TABLE materias (
    id_materia INT AUTO_INCREMENT PRIMARY KEY,
    nombre_materia VARCHAR(100) NOT NULL UNIQUE
);

--E/r nombre Materias con nivel (muchos a muchos)  para evitar repetir datos :3
CREATE TABLE materias_nivel (
    id_materia_nivel INT AUTO_INCREMENT PRIMARY KEY,
    id_materia INT,
    id_nivel INT,
    FOREIGN KEY (id_materia) REFERENCES materias(id_materia),
    FOREIGN KEY (id_nivel) REFERENCES niveles(id_nivel)
);

-- Cargos para empleados
CREATE TABLE cargos (
    id_cargo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cargo VARCHAR(100) NOT NULL UNIQUE,  -- Director, Secretaria, Portero, etc.
    descripcion TEXT
);

-- Tipos de calificación
CREATE TABLE tipos_calificacion (
    id_tipo_calificacion INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL UNIQUE  -- Numerica, Letra
);

-- Tabla base: Personas ( basicamente para todos: estudiantes, profesores, empleados, representantes)
CREATE TABLE personas (
    id_persona INT AUTO_INCREMENT PRIMARY KEY,
    primer_nombre VARCHAR(50) NOT NULL,
    segundo_nombre VARCHAR(50),
    primer_apellido VARCHAR(50) NOT NULL,
    segundo_apellido VARCHAR(50),
    id_tipo_documento INT,
    numero_documento VARCHAR(20) NOT NULL UNIQUE,
    fecha_nacimiento DATE,
    id_sexo INT,
    id_direccion INT,
    id_pais INT,
    id_ciudad INT,
    FOREIGN KEY (id_tipo_documento) REFERENCES tipo_documento(id_tipo_documento),
    FOREIGN KEY (id_sexo) REFERENCES sexo(id_sexo),
    FOREIGN KEY (id_direccion) REFERENCES direcciones(id_direccion),
    FOREIGN KEY (id_pais) REFERENCES nacionalidad(id_pais),
    FOREIGN KEY (id_ciudad) REFERENCES ciudades(id_ciudad)
);

-- Usuarios (para acceso al sistema)
CREATE TABLE usuarios (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    id_contacto INT,
    id_rol INT,
    id_status_user INT,
    id_persona INT,  -- Vincula usuario a persona
    FOREIGN KEY (id_contacto) REFERENCES contactos(id_contacto),
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol),
    FOREIGN KEY (id_status_user) REFERENCES status_user(id_status_user),
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona)
);

-- Estudiantes (extensión de personas)
CREATE TABLE estudiantes (
    id_estudiante INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT,
    fecha_inscripcion DATE NOT NULL,
    id_nivel_actual INT,
    id_seccion_actual INT,
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona),
    FOREIGN KEY (id_nivel_actual) REFERENCES niveles(id_nivel),
    FOREIGN KEY (id_seccion_actual) REFERENCES secciones(id_seccion)
);

-- Profesores (extensión de personas)
CREATE TABLE profesores (
    id_profesor INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT,
    id_especialidad INT,
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona),
    FOREIGN KEY (id_especialidad) REFERENCES especialidades(id_especialidad)
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
CREATE TABLE historial_estudiantes (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT,
    id_nivel_anterior INT NULL,
    id_seccion_anterior INT NULL,
    id_nivel_nuevo INT,
    id_seccion_nuevo INT,
    fecha_cambio DATE NOT NULL,
    motivo VARCHAR(100),
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante),
    FOREIGN KEY (id_nivel_anterior) REFERENCES niveles(id_nivel),
    FOREIGN KEY (id_seccion_anterior) REFERENCES secciones(id_seccion),
    FOREIGN KEY (id_nivel_nuevo) REFERENCES niveles(id_nivel),
    FOREIGN KEY (id_seccion_nuevo) REFERENCES secciones(id_seccion)
);

-- Datos adicionales por persona
CREATE TABLE datos_academicos (
    id_datos_academicos INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT,
    id_nivel_academico INT,
    institucion VARCHAR(100) NOT NULL,
    anio_graduacion YEAR,
    id_profesion INT,
    id_ocupacion INT,
    sabe_leer BOOLEAN,
    sabe_escribir BOOLEAN,
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona),
    FOREIGN KEY (id_nivel_academico) REFERENCES niveles_academicos(id_nivel_academico),
    FOREIGN KEY (id_profesion) REFERENCES profesiones(id_profesion),
    FOREIGN KEY (id_ocupacion) REFERENCES ocupaciones(id_ocupacion)
);

CREATE TABLE datos_economicos (
    id_datos_economicos INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT,
    ingresos_mensuales DECIMAL(10,2),
    fuente_ingresos VARCHAR(100),
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona)
);

CREATE TABLE datos_familiares (
    id_datos_familiares INT AUTO_INCREMENT PRIMARY KEY,
    id_persona INT,
    id_estado_civil INT,
    id_religion INT,
    habilidades TEXT,
    destrezas TEXT,
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

-- Asignaciones de profesores a secciones/materias
CREATE TABLE asignaciones_profesor (
    id_asignacion INT AUTO_INCREMENT PRIMARY KEY,
    id_profesor INT,
    id_seccion INT,
    id_materia INT NULL,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor),
    FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion),
    FOREIGN KEY (id_materia) REFERENCES materias(id_materia)
);

-- Horarios
CREATE TABLE horarios (
    id_horario INT AUTO_INCREMENT PRIMARY KEY,
    id_seccion INT,
    id_materia INT NULL,
    id_profesor INT,
    dia_semana VARCHAR(20) NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion),
    FOREIGN KEY (id_materia) REFERENCES materias(id_materia),
    FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor)
);

-- Calificaciones
CREATE TABLE calificaciones (
    id_calificacion INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT,
    id_materia INT NULL,
    periodo_academico VARCHAR(50) NOT NULL,
    calificacion_numerica DECIMAL(5,2) NULL,
    id_tipo_calificacion INT,
    letra_calificacion CHAR(1) NULL,
    fecha_calificacion DATE,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante),
    FOREIGN KEY (id_materia) REFERENCES materias(id_materia),
    FOREIGN KEY (id_tipo_calificacion) REFERENCES tipos_calificacion(id_tipo_calificacion)
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
    estado_matricula VARCHAR(20) NOT NULL,  -- Activa, Inactiva
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante)
);

-- Evaluaciones adicionales (exámenes, proyectos)
CREATE TABLE evaluaciones (
    id_evaluacion INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante INT,
    id_materia INT,
    nombre_evaluacion VARCHAR(100) NOT NULL,
    fecha_evaluacion DATE,
    calificacion DECIMAL(5,2),
    tipo_evaluacion VARCHAR(50),  -- Examen, Proyecto, Tarea
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante),
    FOREIGN KEY (id_materia) REFERENCES materias(id_materia)
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
    evaluador VARCHAR(100),  -- Nombre del evaluador (director, etc.)
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

-- Cursos/materias o capacitaciones que imparten profesores
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