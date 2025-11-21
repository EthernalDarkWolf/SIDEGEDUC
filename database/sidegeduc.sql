create database sidegeduc;
use sidegeduc;

create table roles(
    id_rol int auto_increment primary key,
    nombre_rol varchar(50) not null unique
);
create table usuarios(
    id_user int auto_increment primary key,
    nombre varchar(50) not null,
    correo varchar(100) not null unique,
    contrasena varchar(255) not null,
    id_rol int,
    foreign key (id_rol) references roles(id_rol)
);
create table users_rol(
    id_user int,
    id_rol int,
    primary key (id_user, id_rol),
    foreign key (id_user) references usuarios(id_user),
    foreign key (id_rol) references roles(id_rol)
);
create table identificacion(
    id_identidad int auto_increment primary key,
    numero_identidad varchar(50) not null unique,
    tipo_identidad varchar(50) not null unique
);
create table estudiantes(
    id_estudiante int auto_increment primary key,
    nombre_estudiante varchar(100) not null,
    apellido_estudiante varchar(100) not null,
    id_usuario int,
    foreign key (id_usuario) references usuarios(id_user),
    id_identidad int,
    id_rol int,
    foreign key (id_rol) references roles(id_rol),
    foreign key (id_identidad) references identificacion(id_identidad)
);
create table representantes(
    id_representante int auto_increment primary key,
    nombre_representante varchar(100) not null,
    apellido_representante varchar(100) not null,
    id_identidad int,
    id_estudiante int,
    foreign key (id_identidad) references identificacion(id_identidad),
    foreign key (id_estudiante) references estudiantes(id_estudiante)
);
create table profesores(
    id_profesor int auto_increment primary key,
    nombre_profesor varchar(100) not null,
    apellido_profesor varchar(100) not null,
    especialidad varchar(100) not null,
    id_identidad int,
    id_rol int,
    id_usuario int,
    foreign key (id_usuario) references usuarios(id_user),
    foreign key (id_identidad) references identificacion(id_identidad),
    foreign key (id_rol) references roles(id_rol)
);
create table materias(
    id_curso int auto_increment primary key,
    nombre_curso varchar(100) not null,
    id_profesor int,
    foreign key (id_profesor) references profesores(id_profesor)
);

create table letra_seccion(
    id_letra_seccion int auto_increment primary key,
    letra_seccion varchar(6) not null unique
);
create table año_seccion(
    id_año_seccion int auto_increment primary key,
    año_seccion varchar(6) not null unique
);
create table secciones(
    id_seccion int auto_increment primary key,
    id_letra_seccion int,
    id_año_seccion int,
    id_estudiante int,
    id_profesor int,
    foreign key (id_profesor) references profesores(id_profesor),
    foreign key (id_estudiante) references estudiantes(id_estudiante),
    foreign key (id_letra_seccion) references letra_seccion(id_letra_seccion),
    foreign key (id_año_seccion) references año_seccion(id_año_seccion)
);

insert into usuarios(nombre, correo, contrasena, id_rol) values
('javier_andueza', 'janzajsc1@gmail.com', 1);