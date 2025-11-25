create database sidegeduc;
use sidegeduc;

create table roles(
    id_rol int auto_increment primary key,
    nombre_rol varchar(50) not null unique
);
create table usuarios(
    id_user int auto_increment primary key,
    nombre varchar(50) not null unique,
    contrasena varchar(255) not null,
    id_rol int,
    foreign key (id_rol) references roles(id_rol)
);

create table status_user(
    id_status_user int auto_increment primary key,
    estado varchar(50) not null unique
    id_user int,
    foreign key (id_user) references usuarios(id_user)
);

insert into roles (nombre_rol) values ('Admin'), ('Profesor'), ('Estudiante');
insert into usuarios (nombre, contrasena, id_rol) values ('Technowolf', '1234'. 1);
insert into status_user (estado, id_user) values ('Activo', 1);