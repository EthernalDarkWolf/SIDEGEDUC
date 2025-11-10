CREATE DATABASE IF NOT EXISTS sidegu CHARACTER SET utf8mb4 COLLATE  utf8mb4_unicode_ci;
USE sidegu;

CREATE TABLE IF NOT EXISTS roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol ENUM('Profesor', 'Estudiante', 'Administrador') UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    nickname VARCHAR(50) UNIQUE NOT NULL,
    ci INT(50) UNIQUE NULL,
    email VARCHAR(150) UNIQUE NULL,
    contrasena VARCHAR(255) NOT NULL,
    id_rol INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS alumnos (
    id_alumno INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT UNIQUE,
    fecha_nacimiento DATE,
    direccion VARCHAR(255),
    telefono VARCHAR(20) NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS profesores (
    id_profesor INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT UNIQUE,
    especialidad VARCHAR(100),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS materias (
    id_curso INT AUTO_INCREMENT PRIMARY KEY,
    nombre_materia VARCHAR(150) UNIQUE NULL,
    descripcion TEXT,
    id_profesor INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS salones (
    id_salon INT AUTO_INCREMENT PRIMARY KEY,
    grado_salon VARCHAR(50) NOT NULL,
    seccion_salon VARCHAR(10) NOT NULL,
    FOREIGN KEY(id_alumno, id_profesor) REFERENCES alumnos(id_alumno), profesores(id_profesor)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE IF NOT EXISTS otro_personal (
    id_personal INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT UNIQUE,
    nombre_persona VARCHAR(70)
    cargo VARCHAR(150),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO roles (nombre_rol) VALUES 
('Profesor'), 
('Estudiante'), 
('Administrador');


