CREATE DATABASE  IF NOT EXISTS `sidegeduc` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `sidegeduc`;
-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: sidegeduc
-- ------------------------------------------------------
-- Server version	5.5.5-10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `asistencia`
--

DROP TABLE IF EXISTS `asistencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `asistencia` (
  `id_asistencia` int(11) NOT NULL AUTO_INCREMENT,
  `id_estudiante` int(11) DEFAULT NULL,
  `fecha` date NOT NULL,
  `estado_asistencia` varchar(20) NOT NULL,
  `id_seccion` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_asistencia`),
  KEY `id_estudiante` (`id_estudiante`),
  KEY `id_seccion` (`id_seccion`),
  CONSTRAINT `asistencia_ibfk_1` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`),
  CONSTRAINT `asistencia_ibfk_2` FOREIGN KEY (`id_seccion`) REFERENCES `secciones` (`id_seccion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `asistencia`
--

LOCK TABLES `asistencia` WRITE;
/*!40000 ALTER TABLE `asistencia` DISABLE KEYS */;
/*!40000 ALTER TABLE `asistencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `calificaciones`
--

DROP TABLE IF EXISTS `calificaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `calificaciones` (
  `id_calificacion` int(11) NOT NULL AUTO_INCREMENT,
  `id_estudiante` int(11) DEFAULT NULL,
  `id_materia_presentada` int(11) DEFAULT NULL,
  `calificacion_en_materia_presentada` decimal(5,2) DEFAULT NULL,
  `rango_letra` int(11) DEFAULT NULL,
  `fecha_calificacion` date DEFAULT NULL,
  `observaciones` text DEFAULT NULL,
  PRIMARY KEY (`id_calificacion`),
  KEY `rango_letra` (`rango_letra`),
  KEY `id_estudiante` (`id_estudiante`),
  KEY `id_materia_presentada` (`id_materia_presentada`),
  CONSTRAINT `calificaciones_ibfk_1` FOREIGN KEY (`rango_letra`) REFERENCES `rangos_calificacion` (`id_rango_calificacion`),
  CONSTRAINT `calificaciones_ibfk_2` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`),
  CONSTRAINT `calificaciones_ibfk_3` FOREIGN KEY (`id_materia_presentada`) REFERENCES `materias` (`id_materia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `calificaciones`
--

LOCK TABLES `calificaciones` WRITE;
/*!40000 ALTER TABLE `calificaciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `calificaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `capacitaciones_profesor`
--

DROP TABLE IF EXISTS `capacitaciones_profesor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `capacitaciones_profesor` (
  `id_capacitacion` int(11) NOT NULL AUTO_INCREMENT,
  `id_profesor` int(11) DEFAULT NULL,
  `nombre_capacitacion` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `duracion_horas` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_capacitacion`),
  KEY `id_profesor` (`id_profesor`),
  CONSTRAINT `capacitaciones_profesor_ibfk_1` FOREIGN KEY (`id_profesor`) REFERENCES `profesores` (`id_profesor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `capacitaciones_profesor`
--

LOCK TABLES `capacitaciones_profesor` WRITE;
/*!40000 ALTER TABLE `capacitaciones_profesor` DISABLE KEYS */;
/*!40000 ALTER TABLE `capacitaciones_profesor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cargos`
--

DROP TABLE IF EXISTS `cargos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cargos` (
  `id_cargo` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_cargo` varchar(100) NOT NULL,
  PRIMARY KEY (`id_cargo`),
  UNIQUE KEY `nombre_cargo` (`nombre_cargo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cargos`
--

LOCK TABLES `cargos` WRITE;
/*!40000 ALTER TABLE `cargos` DISABLE KEYS */;
/*!40000 ALTER TABLE `cargos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `certificaciones_profesor`
--

DROP TABLE IF EXISTS `certificaciones_profesor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `certificaciones_profesor` (
  `id_certificacion` int(11) NOT NULL AUTO_INCREMENT,
  `id_profesor` int(11) DEFAULT NULL,
  `nombre_certificacion` varchar(100) NOT NULL,
  `institucion` varchar(100) DEFAULT NULL,
  `fecha_obtencion` date DEFAULT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  PRIMARY KEY (`id_certificacion`),
  KEY `id_profesor` (`id_profesor`),
  CONSTRAINT `certificaciones_profesor_ibfk_1` FOREIGN KEY (`id_profesor`) REFERENCES `profesores` (`id_profesor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `certificaciones_profesor`
--

LOCK TABLES `certificaciones_profesor` WRITE;
/*!40000 ALTER TABLE `certificaciones_profesor` DISABLE KEYS */;
/*!40000 ALTER TABLE `certificaciones_profesor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ciudades`
--

DROP TABLE IF EXISTS `ciudades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ciudades` (
  `id_ciudad` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_ciudad` varchar(100) NOT NULL,
  PRIMARY KEY (`id_ciudad`),
  UNIQUE KEY `nombre_ciudad` (`nombre_ciudad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ciudades`
--

LOCK TABLES `ciudades` WRITE;
/*!40000 ALTER TABLE `ciudades` DISABLE KEYS */;
/*!40000 ALTER TABLE `ciudades` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contactos`
--

DROP TABLE IF EXISTS `contactos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contactos` (
  `id_contacto` int(11) NOT NULL AUTO_INCREMENT,
  `telefono` varchar(15) NOT NULL,
  `email` varchar(100) NOT NULL,
  PRIMARY KEY (`id_contacto`),
  UNIQUE KEY `telefono` (`telefono`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contactos`
--

LOCK TABLES `contactos` WRITE;
/*!40000 ALTER TABLE `contactos` DISABLE KEYS */;
/*!40000 ALTER TABLE `contactos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `datos_academicos`
--

DROP TABLE IF EXISTS `datos_academicos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `datos_academicos` (
  `id_datos_academicos` int(11) NOT NULL AUTO_INCREMENT,
  `id_persona` int(11) DEFAULT NULL,
  `id_nivel_academico` int(11) DEFAULT NULL,
  `institucion` varchar(100) DEFAULT NULL,
  `anio_graduacion` year(4) DEFAULT NULL,
  `id_profesion` int(11) DEFAULT NULL,
  `id_ocupacion` int(11) DEFAULT NULL,
  `id_especialidad` int(11) DEFAULT NULL,
  `sabe_leer` tinyint(1) DEFAULT NULL,
  `sabe_escribir` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id_datos_academicos`),
  KEY `id_persona` (`id_persona`),
  KEY `id_nivel_academico` (`id_nivel_academico`),
  KEY `id_profesion` (`id_profesion`),
  KEY `id_ocupacion` (`id_ocupacion`),
  KEY `id_especialidad` (`id_especialidad`),
  CONSTRAINT `datos_academicos_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`),
  CONSTRAINT `datos_academicos_ibfk_2` FOREIGN KEY (`id_nivel_academico`) REFERENCES `niveles_academicos` (`id_nivel_academico`),
  CONSTRAINT `datos_academicos_ibfk_3` FOREIGN KEY (`id_profesion`) REFERENCES `profesiones` (`id_profesion`),
  CONSTRAINT `datos_academicos_ibfk_4` FOREIGN KEY (`id_ocupacion`) REFERENCES `ocupaciones` (`id_ocupacion`),
  CONSTRAINT `datos_academicos_ibfk_5` FOREIGN KEY (`id_especialidad`) REFERENCES `especialidades` (`id_especialidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `datos_academicos`
--

LOCK TABLES `datos_academicos` WRITE;
/*!40000 ALTER TABLE `datos_academicos` DISABLE KEYS */;
/*!40000 ALTER TABLE `datos_academicos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `datos_economicos`
--

DROP TABLE IF EXISTS `datos_economicos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `datos_economicos` (
  `id_datos_economicos` int(11) NOT NULL AUTO_INCREMENT,
  `id_persona` int(11) DEFAULT NULL,
  `ingresos_mensuales` decimal(10,2) DEFAULT NULL,
  `id_fuente_ingresos` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_datos_economicos`),
  KEY `id_fuente_ingresos` (`id_fuente_ingresos`),
  KEY `id_persona` (`id_persona`),
  CONSTRAINT `datos_economicos_ibfk_1` FOREIGN KEY (`id_fuente_ingresos`) REFERENCES `fuente_de_ingresos` (`id_fuente_ingresos`),
  CONSTRAINT `datos_economicos_ibfk_2` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `datos_economicos`
--

LOCK TABLES `datos_economicos` WRITE;
/*!40000 ALTER TABLE `datos_economicos` DISABLE KEYS */;
/*!40000 ALTER TABLE `datos_economicos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `datos_familiares`
--

DROP TABLE IF EXISTS `datos_familiares`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `datos_familiares` (
  `id_datos_familiares` int(11) NOT NULL AUTO_INCREMENT,
  `id_persona` int(11) DEFAULT NULL,
  `id_estado_civil` int(11) DEFAULT NULL,
  `id_religion` int(11) DEFAULT NULL,
  `numero_hijos_o_representados` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_datos_familiares`),
  KEY `id_persona` (`id_persona`),
  KEY `id_estado_civil` (`id_estado_civil`),
  KEY `id_religion` (`id_religion`),
  CONSTRAINT `datos_familiares_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`),
  CONSTRAINT `datos_familiares_ibfk_2` FOREIGN KEY (`id_estado_civil`) REFERENCES `estados_civiles` (`id_estado_civil`),
  CONSTRAINT `datos_familiares_ibfk_3` FOREIGN KEY (`id_religion`) REFERENCES `religiones` (`id_religion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `datos_familiares`
--

LOCK TABLES `datos_familiares` WRITE;
/*!40000 ALTER TABLE `datos_familiares` DISABLE KEYS */;
/*!40000 ALTER TABLE `datos_familiares` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `direcciones`
--

DROP TABLE IF EXISTS `direcciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `direcciones` (
  `id_direccion` int(11) NOT NULL AUTO_INCREMENT,
  `direccion` text NOT NULL,
  `id_ciudad` int(11) DEFAULT NULL,
  `id_pais` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_direccion`),
  KEY `id_ciudad` (`id_ciudad`),
  KEY `id_pais` (`id_pais`),
  CONSTRAINT `direcciones_ibfk_1` FOREIGN KEY (`id_ciudad`) REFERENCES `ciudades` (`id_ciudad`),
  CONSTRAINT `direcciones_ibfk_2` FOREIGN KEY (`id_pais`) REFERENCES `nacionalidad` (`id_pais`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `direcciones`
--

LOCK TABLES `direcciones` WRITE;
/*!40000 ALTER TABLE `direcciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `direcciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empleados`
--

DROP TABLE IF EXISTS `empleados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empleados` (
  `id_empleado` int(11) NOT NULL AUTO_INCREMENT,
  `id_persona` int(11) DEFAULT NULL,
  `id_cargo` int(11) DEFAULT NULL,
  `fecha_contratacion` date DEFAULT NULL,
  `salario` decimal(10,2) DEFAULT NULL,
  `id_plantel` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_empleado`),
  KEY `id_persona` (`id_persona`),
  KEY `id_cargo` (`id_cargo`),
  KEY `fk_empleado_plantel` (`id_plantel`),
  CONSTRAINT `empleados_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`),
  CONSTRAINT `empleados_ibfk_2` FOREIGN KEY (`id_cargo`) REFERENCES `cargos` (`id_cargo`),
  CONSTRAINT `fk_empleado_plantel` FOREIGN KEY (`id_plantel`) REFERENCES `planteles` (`id_plantel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleados`
--

LOCK TABLES `empleados` WRITE;
/*!40000 ALTER TABLE `empleados` DISABLE KEYS */;
/*!40000 ALTER TABLE `empleados` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `especialidades`
--

DROP TABLE IF EXISTS `especialidades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `especialidades` (
  `id_especialidad` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_especialidad` varchar(100) NOT NULL,
  PRIMARY KEY (`id_especialidad`),
  UNIQUE KEY `nombre_especialidad` (`nombre_especialidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `especialidades`
--

LOCK TABLES `especialidades` WRITE;
/*!40000 ALTER TABLE `especialidades` DISABLE KEYS */;
/*!40000 ALTER TABLE `especialidades` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estados_civiles`
--

DROP TABLE IF EXISTS `estados_civiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estados_civiles` (
  `id_estado_civil` int(11) NOT NULL AUTO_INCREMENT,
  `descripcion_estado_civil` varchar(50) NOT NULL,
  PRIMARY KEY (`id_estado_civil`),
  UNIQUE KEY `descripcion_estado_civil` (`descripcion_estado_civil`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estados_civiles`
--

LOCK TABLES `estados_civiles` WRITE;
/*!40000 ALTER TABLE `estados_civiles` DISABLE KEYS */;
/*!40000 ALTER TABLE `estados_civiles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estudiante_representante`
--

DROP TABLE IF EXISTS `estudiante_representante`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estudiante_representante` (
  `id_estudiante_representante` int(11) NOT NULL AUTO_INCREMENT,
  `id_estudiante` int(11) DEFAULT NULL,
  `id_representante` int(11) DEFAULT NULL,
  `es_representante_principal` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id_estudiante_representante`),
  KEY `id_estudiante` (`id_estudiante`),
  KEY `id_representante` (`id_representante`),
  CONSTRAINT `estudiante_representante_ibfk_1` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`),
  CONSTRAINT `estudiante_representante_ibfk_2` FOREIGN KEY (`id_representante`) REFERENCES `representantes` (`id_representante`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estudiante_representante`
--

LOCK TABLES `estudiante_representante` WRITE;
/*!40000 ALTER TABLE `estudiante_representante` DISABLE KEYS */;
/*!40000 ALTER TABLE `estudiante_representante` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estudiante_seccion`
--

DROP TABLE IF EXISTS `estudiante_seccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estudiante_seccion` (
  `id_estudiante_seccion` int(11) NOT NULL AUTO_INCREMENT,
  `id_estudiante` int(11) NOT NULL,
  `id_seccion` int(11) NOT NULL,
  PRIMARY KEY (`id_estudiante_seccion`),
  KEY `id_estudiante` (`id_estudiante`),
  KEY `id_seccion` (`id_seccion`),
  CONSTRAINT `estudiante_seccion_ibfk_1` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`),
  CONSTRAINT `estudiante_seccion_ibfk_2` FOREIGN KEY (`id_seccion`) REFERENCES `secciones` (`id_seccion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estudiante_seccion`
--

LOCK TABLES `estudiante_seccion` WRITE;
/*!40000 ALTER TABLE `estudiante_seccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `estudiante_seccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estudiantes`
--

DROP TABLE IF EXISTS `estudiantes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estudiantes` (
  `id_estudiante` int(11) NOT NULL AUTO_INCREMENT,
  `id_persona` int(11) DEFAULT NULL,
  `fecha_inscripcion` date NOT NULL,
  PRIMARY KEY (`id_estudiante`),
  KEY `id_persona` (`id_persona`),
  CONSTRAINT `estudiantes_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estudiantes`
--

LOCK TABLES `estudiantes` WRITE;
/*!40000 ALTER TABLE `estudiantes` DISABLE KEYS */;
/*!40000 ALTER TABLE `estudiantes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evaluaciones`
--

DROP TABLE IF EXISTS `evaluaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evaluaciones` (
  `id_evaluacion` int(11) NOT NULL AUTO_INCREMENT,
  `id_estudiante` int(11) DEFAULT NULL,
  `materia_adicional` int(11) DEFAULT NULL,
  `nombre_evaluacion` varchar(100) NOT NULL,
  `fecha_evaluacion` date DEFAULT NULL,
  `tipo_evaluacion` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_evaluacion`),
  KEY `id_estudiante` (`id_estudiante`),
  KEY `materia_adicional` (`materia_adicional`),
  CONSTRAINT `evaluaciones_ibfk_1` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`),
  CONSTRAINT `evaluaciones_ibfk_2` FOREIGN KEY (`materia_adicional`) REFERENCES `materias` (`id_materia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evaluaciones`
--

LOCK TABLES `evaluaciones` WRITE;
/*!40000 ALTER TABLE `evaluaciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `evaluaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evaluaciones_profesor`
--

DROP TABLE IF EXISTS `evaluaciones_profesor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evaluaciones_profesor` (
  `id_evaluacion_profesor` int(11) NOT NULL AUTO_INCREMENT,
  `id_profesor` int(11) DEFAULT NULL,
  `fecha_evaluacion` date NOT NULL,
  `evaluador` varchar(100) DEFAULT NULL,
  `puntuacion` decimal(2,1) DEFAULT NULL,
  `comentarios` text DEFAULT NULL,
  PRIMARY KEY (`id_evaluacion_profesor`),
  KEY `id_profesor` (`id_profesor`),
  CONSTRAINT `evaluaciones_profesor_ibfk_1` FOREIGN KEY (`id_profesor`) REFERENCES `profesores` (`id_profesor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evaluaciones_profesor`
--

LOCK TABLES `evaluaciones_profesor` WRITE;
/*!40000 ALTER TABLE `evaluaciones_profesor` DISABLE KEYS */;
/*!40000 ALTER TABLE `evaluaciones_profesor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `experiencia_profesor`
--

DROP TABLE IF EXISTS `experiencia_profesor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `experiencia_profesor` (
  `id_experiencia` int(11) NOT NULL AUTO_INCREMENT,
  `id_profesor` int(11) DEFAULT NULL,
  `institucion` varchar(100) NOT NULL,
  `cargo` varchar(100) NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  PRIMARY KEY (`id_experiencia`),
  KEY `id_profesor` (`id_profesor`),
  CONSTRAINT `experiencia_profesor_ibfk_1` FOREIGN KEY (`id_profesor`) REFERENCES `profesores` (`id_profesor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `experiencia_profesor`
--

LOCK TABLES `experiencia_profesor` WRITE;
/*!40000 ALTER TABLE `experiencia_profesor` DISABLE KEYS */;
/*!40000 ALTER TABLE `experiencia_profesor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuente_de_ingresos`
--

DROP TABLE IF EXISTS `fuente_de_ingresos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fuente_de_ingresos` (
  `id_fuente_ingresos` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_fuente` varchar(100) NOT NULL,
  PRIMARY KEY (`id_fuente_ingresos`),
  UNIQUE KEY `nombre_fuente` (`nombre_fuente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuente_de_ingresos`
--

LOCK TABLES `fuente_de_ingresos` WRITE;
/*!40000 ALTER TABLE `fuente_de_ingresos` DISABLE KEYS */;
/*!40000 ALTER TABLE `fuente_de_ingresos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grados`
--

DROP TABLE IF EXISTS `grados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grados` (
  `id_grado` int(11) NOT NULL AUTO_INCREMENT,
  `numero_grado` tinyint(4) NOT NULL,
  PRIMARY KEY (`id_grado`),
  UNIQUE KEY `numero_grado` (`numero_grado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grados`
--

LOCK TABLES `grados` WRITE;
/*!40000 ALTER TABLE `grados` DISABLE KEYS */;
/*!40000 ALTER TABLE `grados` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial_estudiantes`
--

DROP TABLE IF EXISTS `historial_estudiantes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_estudiantes` (
  `id_historial` int(11) NOT NULL AUTO_INCREMENT,
  `id_estudiante` int(11) DEFAULT NULL,
  `id_seccion_anterior` int(11) DEFAULT NULL,
  `id_seccion_nuevo` int(11) DEFAULT NULL,
  `fecha_cambio` date NOT NULL,
  `id_motivo_del_cambio` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_historial`),
  KEY `id_estudiante` (`id_estudiante`),
  KEY `id_seccion_anterior` (`id_seccion_anterior`),
  KEY `id_seccion_nuevo` (`id_seccion_nuevo`),
  KEY `id_motivo_del_cambio` (`id_motivo_del_cambio`),
  CONSTRAINT `historial_estudiantes_ibfk_1` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`),
  CONSTRAINT `historial_estudiantes_ibfk_2` FOREIGN KEY (`id_seccion_anterior`) REFERENCES `secciones` (`id_seccion`),
  CONSTRAINT `historial_estudiantes_ibfk_3` FOREIGN KEY (`id_seccion_nuevo`) REFERENCES `secciones` (`id_seccion`),
  CONSTRAINT `historial_estudiantes_ibfk_4` FOREIGN KEY (`id_motivo_del_cambio`) REFERENCES `motivos_cambio_seccion` (`id_motivo_cambio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_estudiantes`
--

LOCK TABLES `historial_estudiantes` WRITE;
/*!40000 ALTER TABLE `historial_estudiantes` DISABLE KEYS */;
/*!40000 ALTER TABLE `historial_estudiantes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `horarios`
--

DROP TABLE IF EXISTS `horarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `horarios` (
  `id_horario` int(11) NOT NULL AUTO_INCREMENT,
  `id_seccion` int(11) DEFAULT NULL,
  `id_materia` int(11) DEFAULT NULL,
  `dia_semana` varchar(20) NOT NULL,
  `hora_inicio` time NOT NULL,
  `hora_fin` time NOT NULL,
  PRIMARY KEY (`id_horario`),
  KEY `id_seccion` (`id_seccion`),
  KEY `id_materia` (`id_materia`),
  CONSTRAINT `horarios_ibfk_1` FOREIGN KEY (`id_seccion`) REFERENCES `secciones` (`id_seccion`),
  CONSTRAINT `horarios_ibfk_2` FOREIGN KEY (`id_materia`) REFERENCES `materias` (`id_materia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `horarios`
--

LOCK TABLES `horarios` WRITE;
/*!40000 ALTER TABLE `horarios` DISABLE KEYS */;
/*!40000 ALTER TABLE `horarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `identificaciones`
--

DROP TABLE IF EXISTS `identificaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `identificaciones` (
  `id_identificacion` int(11) NOT NULL AUTO_INCREMENT,
  `id_persona` int(11) NOT NULL,
  `id_tipo_documento` int(11) DEFAULT NULL,
  `categoria` enum('ciudadana','escolar') NOT NULL COMMENT 'ciudadana: cedula nacional; escolar: cedula escolar asociada a representante',
  `numero_identificacion` varchar(100) NOT NULL,
  `fecha_emision` date DEFAULT NULL,
  `vigente` tinyint(1) DEFAULT 1,
  `id_representante` int(11) DEFAULT NULL,
  `informacion_adicional` text DEFAULT NULL,
  PRIMARY KEY (`id_identificacion`),
  UNIQUE KEY `uq_persona_categoria` (`id_persona`,`categoria`),
  UNIQUE KEY `uq_numero_identificacion` (`numero_identificacion`),
  KEY `id_tipo_documento` (`id_tipo_documento`),
  KEY `id_representante` (`id_representante`),
  CONSTRAINT `identificaciones_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`),
  CONSTRAINT `identificaciones_ibfk_2` FOREIGN KEY (`id_tipo_documento`) REFERENCES `tipo_documento` (`id_tipo_documento`),
  CONSTRAINT `identificaciones_ibfk_3` FOREIGN KEY (`id_representante`) REFERENCES `representantes` (`id_representante`),
  CONSTRAINT `CONSTRAINT_1` CHECK (`categoria` <> 'escolar' or `id_representante` is not null)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `identificaciones`
--

LOCK TABLES `identificaciones` WRITE;
/*!40000 ALTER TABLE `identificaciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `identificaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `letra_seccion`
--

DROP TABLE IF EXISTS `letra_seccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `letra_seccion` (
  `id_letra_seccion` int(11) NOT NULL AUTO_INCREMENT,
  `letra` char(1) NOT NULL,
  PRIMARY KEY (`id_letra_seccion`),
  UNIQUE KEY `letra` (`letra`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `letra_seccion`
--

LOCK TABLES `letra_seccion` WRITE;
/*!40000 ALTER TABLE `letra_seccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `letra_seccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `materias`
--

DROP TABLE IF EXISTS `materias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `materias` (
  `id_materia` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_materia` varchar(100) NOT NULL,
  PRIMARY KEY (`id_materia`),
  UNIQUE KEY `nombre_materia` (`nombre_materia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `materias`
--

LOCK TABLES `materias` WRITE;
/*!40000 ALTER TABLE `materias` DISABLE KEYS */;
/*!40000 ALTER TABLE `materias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `materias_seccion`
--

DROP TABLE IF EXISTS `materias_seccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `materias_seccion` (
  `id_materia_nivel` int(11) NOT NULL AUTO_INCREMENT,
  `id_materia` int(11) DEFAULT NULL,
  `id_seccion` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_materia_nivel`),
  KEY `id_seccion` (`id_seccion`),
  KEY `id_materia` (`id_materia`),
  CONSTRAINT `materias_seccion_ibfk_1` FOREIGN KEY (`id_seccion`) REFERENCES `secciones` (`id_seccion`),
  CONSTRAINT `materias_seccion_ibfk_2` FOREIGN KEY (`id_materia`) REFERENCES `materias` (`id_materia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `materias_seccion`
--

LOCK TABLES `materias_seccion` WRITE;
/*!40000 ALTER TABLE `materias_seccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `materias_seccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `matriculas`
--

DROP TABLE IF EXISTS `matriculas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `matriculas` (
  `id_matricula` int(11) NOT NULL AUTO_INCREMENT,
  `id_estudiante` int(11) DEFAULT NULL,
  `anio_academico` year(4) NOT NULL,
  `fecha_matricula` date NOT NULL,
  `monto_matricula` decimal(10,2) DEFAULT NULL,
  `pago_realizado` tinyint(1) DEFAULT 0,
  `estado_matricula` varchar(20) NOT NULL,
  PRIMARY KEY (`id_matricula`),
  KEY `id_estudiante` (`id_estudiante`),
  CONSTRAINT `matriculas_ibfk_1` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `matriculas`
--

LOCK TABLES `matriculas` WRITE;
/*!40000 ALTER TABLE `matriculas` DISABLE KEYS */;
/*!40000 ALTER TABLE `matriculas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `motivos_cambio_seccion`
--

DROP TABLE IF EXISTS `motivos_cambio_seccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `motivos_cambio_seccion` (
  `id_motivo_cambio` int(11) NOT NULL AUTO_INCREMENT,
  `descripcion_motivo` varchar(100) NOT NULL,
  PRIMARY KEY (`id_motivo_cambio`),
  UNIQUE KEY `descripcion_motivo` (`descripcion_motivo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `motivos_cambio_seccion`
--

LOCK TABLES `motivos_cambio_seccion` WRITE;
/*!40000 ALTER TABLE `motivos_cambio_seccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `motivos_cambio_seccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `nacionalidad`
--

DROP TABLE IF EXISTS `nacionalidad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nacionalidad` (
  `id_pais` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_pais` varchar(100) NOT NULL,
  PRIMARY KEY (`id_pais`),
  UNIQUE KEY `nombre_pais` (`nombre_pais`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nacionalidad`
--

LOCK TABLES `nacionalidad` WRITE;
/*!40000 ALTER TABLE `nacionalidad` DISABLE KEYS */;
/*!40000 ALTER TABLE `nacionalidad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `niveles`
--

DROP TABLE IF EXISTS `niveles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `niveles` (
  `id_nivel` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_nivel` varchar(50) NOT NULL,
  PRIMARY KEY (`id_nivel`),
  UNIQUE KEY `nombre_nivel` (`nombre_nivel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `niveles`
--

LOCK TABLES `niveles` WRITE;
/*!40000 ALTER TABLE `niveles` DISABLE KEYS */;
/*!40000 ALTER TABLE `niveles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `niveles_academicos`
--

DROP TABLE IF EXISTS `niveles_academicos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `niveles_academicos` (
  `id_nivel_academico` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_nivel_academico` varchar(100) NOT NULL,
  PRIMARY KEY (`id_nivel_academico`),
  UNIQUE KEY `nombre_nivel_academico` (`nombre_nivel_academico`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `niveles_academicos`
--

LOCK TABLES `niveles_academicos` WRITE;
/*!40000 ALTER TABLE `niveles_academicos` DISABLE KEYS */;
/*!40000 ALTER TABLE `niveles_academicos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ocupaciones`
--

DROP TABLE IF EXISTS `ocupaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ocupaciones` (
  `id_ocupacion` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_ocupacion` varchar(100) NOT NULL,
  PRIMARY KEY (`id_ocupacion`),
  UNIQUE KEY `nombre_ocupacion` (`nombre_ocupacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ocupaciones`
--

LOCK TABLES `ocupaciones` WRITE;
/*!40000 ALTER TABLE `ocupaciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `ocupaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `persona_contacto`
--

DROP TABLE IF EXISTS `persona_contacto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `persona_contacto` (
  `id_persona_contacto` int(11) NOT NULL AUTO_INCREMENT,
  `id_persona` int(11) DEFAULT NULL,
  `id_contacto` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_persona_contacto`),
  KEY `id_persona` (`id_persona`),
  KEY `id_contacto` (`id_contacto`),
  CONSTRAINT `persona_contacto_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`),
  CONSTRAINT `persona_contacto_ibfk_2` FOREIGN KEY (`id_contacto`) REFERENCES `contactos` (`id_contacto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `persona_contacto`
--

LOCK TABLES `persona_contacto` WRITE;
/*!40000 ALTER TABLE `persona_contacto` DISABLE KEYS */;
/*!40000 ALTER TABLE `persona_contacto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `personas`
--

DROP TABLE IF EXISTS `personas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `personas` (
  `id_persona` int(11) NOT NULL AUTO_INCREMENT,
  `primer_nombre` varchar(50) NOT NULL,
  `segundo_nombre` varchar(50) DEFAULT NULL,
  `primer_apellido` varchar(50) NOT NULL,
  `segundo_apellido` varchar(50) DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `id_sexo` int(11) DEFAULT NULL,
  `tipo_persona` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_persona`),
  KEY `id_sexo` (`id_sexo`),
  CONSTRAINT `personas_ibfk_1` FOREIGN KEY (`id_sexo`) REFERENCES `sexo` (`id_sexo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `personas`
--

LOCK TABLES `personas` WRITE;
/*!40000 ALTER TABLE `personas` DISABLE KEYS */;
/*!40000 ALTER TABLE `personas` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_ZERO_IN_DATE,NO_ZERO_DATE,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER trg_persona_alcanzar_edad_ciudadana
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
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `planteles`
--

DROP TABLE IF EXISTS `planteles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `planteles` (
  `id_plantel` int(11) NOT NULL AUTO_INCREMENT,
  `ccid_estado` varchar(100) DEFAULT NULL,
  `estado` varchar(100) DEFAULT NULL,
  `municipio` varchar(100) DEFAULT NULL,
  `parroquia` varchar(100) DEFAULT NULL,
  `codigo_dependencia` varchar(100) DEFAULT NULL,
  `codigo_estadistico` varchar(100) DEFAULT NULL,
  `codigo_plantel` varchar(100) DEFAULT NULL,
  `nombre_plantel_nomina` varchar(200) DEFAULT NULL,
  `id_nivel` int(11) DEFAULT NULL,
  `modalidad` varchar(100) DEFAULT NULL,
  `ubicacion_geografica` enum('Rural','Urbana') DEFAULT NULL,
  `turnos` varchar(200) DEFAULT NULL,
  `codigo_pa` varchar(100) NOT NULL,
  `id_cargo` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_plantel`),
  UNIQUE KEY `codigo_pa` (`codigo_pa`),
  KEY `id_nivel` (`id_nivel`),
  KEY `id_cargo` (`id_cargo`),
  CONSTRAINT `planteles_ibfk_1` FOREIGN KEY (`id_nivel`) REFERENCES `niveles` (`id_nivel`),
  CONSTRAINT `planteles_ibfk_2` FOREIGN KEY (`id_cargo`) REFERENCES `cargos` (`id_cargo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `planteles`
--

LOCK TABLES `planteles` WRITE;
/*!40000 ALTER TABLE `planteles` DISABLE KEYS */;
/*!40000 ALTER TABLE `planteles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profesiones`
--

DROP TABLE IF EXISTS `profesiones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `profesiones` (
  `id_profesion` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_profesion` varchar(100) NOT NULL,
  PRIMARY KEY (`id_profesion`),
  UNIQUE KEY `nombre_profesion` (`nombre_profesion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profesiones`
--

LOCK TABLES `profesiones` WRITE;
/*!40000 ALTER TABLE `profesiones` DISABLE KEYS */;
/*!40000 ALTER TABLE `profesiones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profesor_empleado`
--

DROP TABLE IF EXISTS `profesor_empleado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `profesor_empleado` (
  `id_profesor_empleado` int(11) NOT NULL AUTO_INCREMENT,
  `id_profesor` int(11) DEFAULT NULL,
  `id_empleado` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_profesor_empleado`),
  KEY `id_profesor` (`id_profesor`),
  KEY `id_empleado` (`id_empleado`),
  CONSTRAINT `profesor_empleado_ibfk_1` FOREIGN KEY (`id_profesor`) REFERENCES `profesores` (`id_profesor`),
  CONSTRAINT `profesor_empleado_ibfk_2` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profesor_empleado`
--

LOCK TABLES `profesor_empleado` WRITE;
/*!40000 ALTER TABLE `profesor_empleado` DISABLE KEYS */;
/*!40000 ALTER TABLE `profesor_empleado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profesor_seccion`
--

DROP TABLE IF EXISTS `profesor_seccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `profesor_seccion` (
  `id_profesor_seccion` int(11) NOT NULL AUTO_INCREMENT,
  `id_profesor` int(11) NOT NULL,
  `id_seccion` int(11) NOT NULL,
  PRIMARY KEY (`id_profesor_seccion`),
  KEY `id_profesor` (`id_profesor`),
  KEY `id_seccion` (`id_seccion`),
  CONSTRAINT `profesor_seccion_ibfk_1` FOREIGN KEY (`id_profesor`) REFERENCES `profesores` (`id_profesor`),
  CONSTRAINT `profesor_seccion_ibfk_2` FOREIGN KEY (`id_seccion`) REFERENCES `secciones` (`id_seccion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profesor_seccion`
--

LOCK TABLES `profesor_seccion` WRITE;
/*!40000 ALTER TABLE `profesor_seccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `profesor_seccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profesores`
--

DROP TABLE IF EXISTS `profesores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `profesores` (
  `id_profesor` int(11) NOT NULL AUTO_INCREMENT,
  `id_persona` int(11) DEFAULT NULL,
  `id_especialidad` int(11) DEFAULT NULL,
  `tipo_docente` varchar(100) DEFAULT NULL,
  `id_plantel` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_profesor`),
  KEY `id_persona` (`id_persona`),
  KEY `id_especialidad` (`id_especialidad`),
  KEY `fk_profesor_plantel` (`id_plantel`),
  CONSTRAINT `fk_profesor_plantel` FOREIGN KEY (`id_plantel`) REFERENCES `planteles` (`id_plantel`),
  CONSTRAINT `profesores_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`),
  CONSTRAINT `profesores_ibfk_2` FOREIGN KEY (`id_especialidad`) REFERENCES `especialidades` (`id_especialidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profesores`
--

LOCK TABLES `profesores` WRITE;
/*!40000 ALTER TABLE `profesores` DISABLE KEYS */;
/*!40000 ALTER TABLE `profesores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rangos_calificacion`
--

DROP TABLE IF EXISTS `rangos_calificacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rangos_calificacion` (
  `id_rango_calificacion` int(11) NOT NULL AUTO_INCREMENT,
  `rango_letra` char(1) NOT NULL,
  PRIMARY KEY (`id_rango_calificacion`),
  UNIQUE KEY `rango_letra` (`rango_letra`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rangos_calificacion`
--

LOCK TABLES `rangos_calificacion` WRITE;
/*!40000 ALTER TABLE `rangos_calificacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `rangos_calificacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `religiones`
--

DROP TABLE IF EXISTS `religiones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `religiones` (
  `id_religion` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_religion` varchar(100) NOT NULL,
  PRIMARY KEY (`id_religion`),
  UNIQUE KEY `nombre_religion` (`nombre_religion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `religiones`
--

LOCK TABLES `religiones` WRITE;
/*!40000 ALTER TABLE `religiones` DISABLE KEYS */;
/*!40000 ALTER TABLE `religiones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `representantes`
--

DROP TABLE IF EXISTS `representantes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `representantes` (
  `id_representante` int(11) NOT NULL AUTO_INCREMENT,
  `id_persona` int(11) DEFAULT NULL,
  `ocupacion` varchar(100) DEFAULT NULL,
  `relacion_con_estudiante` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_representante`),
  KEY `id_persona` (`id_persona`),
  CONSTRAINT `representantes_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `representantes`
--

LOCK TABLES `representantes` WRITE;
/*!40000 ALTER TABLE `representantes` DISABLE KEYS */;
/*!40000 ALTER TABLE `representantes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id_rol` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_rol` varchar(50) NOT NULL,
  PRIMARY KEY (`id_rol`),
  UNIQUE KEY `nombre_rol` (`nombre_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Desarrollador'),(3,'Docente'),(6,'Empleado Administrativo'),(5,'Estudiante'),(4,'Representante');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `secciones`
--

DROP TABLE IF EXISTS `secciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `secciones` (
  `id_seccion` int(11) NOT NULL AUTO_INCREMENT,
  `id_letra_seccion` int(11) DEFAULT NULL,
  `id_grado` int(11) DEFAULT NULL,
  `id_nivel` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_seccion`),
  KEY `id_grado` (`id_grado`),
  KEY `id_letra_seccion` (`id_letra_seccion`),
  KEY `id_nivel` (`id_nivel`),
  CONSTRAINT `secciones_ibfk_1` FOREIGN KEY (`id_grado`) REFERENCES `grados` (`id_grado`),
  CONSTRAINT `secciones_ibfk_2` FOREIGN KEY (`id_letra_seccion`) REFERENCES `letra_seccion` (`id_letra_seccion`),
  CONSTRAINT `secciones_ibfk_3` FOREIGN KEY (`id_nivel`) REFERENCES `niveles` (`id_nivel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `secciones`
--

LOCK TABLES `secciones` WRITE;
/*!40000 ALTER TABLE `secciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `secciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sexo`
--

DROP TABLE IF EXISTS `sexo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sexo` (
  `id_sexo` int(11) NOT NULL AUTO_INCREMENT,
  `letra_sexo` char(1) NOT NULL,
  PRIMARY KEY (`id_sexo`),
  UNIQUE KEY `letra_sexo` (`letra_sexo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sexo`
--

LOCK TABLES `sexo` WRITE;
/*!40000 ALTER TABLE `sexo` DISABLE KEYS */;
/*!40000 ALTER TABLE `sexo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `status_user`
--

DROP TABLE IF EXISTS `status_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `status_user` (
  `id_status_user` int(11) NOT NULL AUTO_INCREMENT,
  `estado` varchar(50) NOT NULL,
  PRIMARY KEY (`id_status_user`),
  UNIQUE KEY `estado` (`estado`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `status_user`
--

LOCK TABLES `status_user` WRITE;
/*!40000 ALTER TABLE `status_user` DISABLE KEYS */;
INSERT INTO `status_user` VALUES (1,'activo'),(2,'inactivo'),(3,'suspendido');
/*!40000 ALTER TABLE `status_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipo_documento`
--

DROP TABLE IF EXISTS `tipo_documento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipo_documento` (
  `id_tipo_documento` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_tipo_documento` varchar(50) NOT NULL,
  PRIMARY KEY (`id_tipo_documento`),
  UNIQUE KEY `nombre_tipo_documento` (`nombre_tipo_documento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipo_documento`
--

LOCK TABLES `tipo_documento` WRITE;
/*!40000 ALTER TABLE `tipo_documento` DISABLE KEYS */;
/*!40000 ALTER TABLE `tipo_documento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipos_calificacion`
--

DROP TABLE IF EXISTS `tipos_calificacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipos_calificacion` (
  `id_tipo_calificacion` int(11) NOT NULL AUTO_INCREMENT,
  `tipo` varchar(20) NOT NULL,
  PRIMARY KEY (`id_tipo_calificacion`),
  UNIQUE KEY `tipo` (`tipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipos_calificacion`
--

LOCK TABLES `tipos_calificacion` WRITE;
/*!40000 ALTER TABLE `tipos_calificacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `tipos_calificacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tutorias`
--

DROP TABLE IF EXISTS `tutorias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tutorias` (
  `id_tutoria` int(11) NOT NULL AUTO_INCREMENT,
  `id_profesor` int(11) DEFAULT NULL,
  `id_estudiante` int(11) DEFAULT NULL,
  `tipo_tutoria` varchar(50) DEFAULT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  PRIMARY KEY (`id_tutoria`),
  KEY `id_profesor` (`id_profesor`),
  KEY `id_estudiante` (`id_estudiante`),
  CONSTRAINT `tutorias_ibfk_1` FOREIGN KEY (`id_profesor`) REFERENCES `profesores` (`id_profesor`),
  CONSTRAINT `tutorias_ibfk_2` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tutorias`
--

LOCK TABLES `tutorias` WRITE;
/*!40000 ALTER TABLE `tutorias` DISABLE KEYS */;
/*!40000 ALTER TABLE `tutorias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario_persona`
--

DROP TABLE IF EXISTS `usuario_persona`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario_persona` (
  `id_usuario_persona` int(11) NOT NULL AUTO_INCREMENT,
  `id_user` int(11) DEFAULT NULL,
  `id_persona` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_usuario_persona`),
  KEY `id_user` (`id_user`),
  KEY `id_persona` (`id_persona`),
  CONSTRAINT `usuario_persona_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `usuarios` (`id_user`),
  CONSTRAINT `usuario_persona_ibfk_2` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario_persona`
--

LOCK TABLES `usuario_persona` WRITE;
/*!40000 ALTER TABLE `usuario_persona` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuario_persona` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id_user` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `id_rol` int(11) DEFAULT NULL,
  `id_status_user` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_user`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `id_rol` (`id_rol`),
  KEY `id_status_user` (`id_status_user`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `roles` (`id_rol`),
  CONSTRAINT `usuarios_ibfk_2` FOREIGN KEY (`id_status_user`) REFERENCES `status_user` (`id_status_user`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'Lobito','162618',1,1),(2,'admin2','162618',1,2),(3,'prueba','scrypt:32768:8:1$YkIOjhagNjjBHLYV$88232eea10fa3ddeab09618704ddb8e50027c5a607db7d0462c05b7c6ddc100254ff662ad8bf88459f80e39ed32c0c3a568eee3c92ae00fa25ec0ae794ba76bd',1,1),(4,'Juan','scrypt:32768:8:1$F2JxMDHEhzbWO53j$e5fd39af180aaafd878d793b8266d82bd15873cde1834bbf44ff2d0e0eaccbdde88bf34812de258bd80b38d782fff43ed45138298ee3f0588deae6521379c5df',1,1),(5,'Carmen','scrypt:32768:8:1$qpKqyTcevrpiynix$00b7c40e15ee05d9040552cc1f1af91d76a9bd0dcdab4b4878c3326c0e894005653800a6093f6f5a7b0ee826b858b3209977bd147bbadfa548eed62c4fe66ea2',1,1);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'sidegeduc'
--

--
-- Dumping routines for database 'sidegeduc'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-23 14:31:58
