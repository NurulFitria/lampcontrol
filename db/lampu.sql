-- MySQL dump 10.13  Distrib 5.5.25a, for Linux (i686)
--
-- Host: localhost    Database: lampu
-- ------------------------------------------------------
-- Server version	5.5.25a

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `jadwal`
--

DROP TABLE IF EXISTS `jadwal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jadwal` (
  `id_jadwal` varchar(5) NOT NULL DEFAULT '',
  `hari` varchar(20) DEFAULT NULL,
  `mulai` time NOT NULL DEFAULT '00:00:00',
  `selesai` time NOT NULL DEFAULT '00:00:00',
  PRIMARY KEY (`id_jadwal`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jadwal`
--

LOCK TABLES `jadwal` WRITE;
/*!40000 ALTER TABLE `jadwal` DISABLE KEYS */;
INSERT INTO `jadwal` VALUES ('001','Kamis','18:00:00','19:00:00'),('002','Kamis','00:00:00','06:00:00'),('003','Kamis','16:00:00','17:00:00');
/*!40000 ALTER TABLE `jadwal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lampu`
--

DROP TABLE IF EXISTS `lampu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lampu` (
  `id_lampu` varchar(3) NOT NULL DEFAULT '',
  `nama_lampu` varchar(20) DEFAULT NULL,
  `pin` int(2) DEFAULT NULL,
  `status` varchar(3) NOT NULL,
  PRIMARY KEY (`id_lampu`),
  UNIQUE KEY `id_lampu` (`id_lampu`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lampu`
--

LOCK TABLES `lampu` WRITE;
/*!40000 ALTER TABLE `lampu` DISABLE KEYS */;
INSERT INTO `lampu` VALUES ('1','quality control',1,'off');
/*!40000 ALTER TABLE `lampu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `log`
--

DROP TABLE IF EXISTS `log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `log` (
  `tanggal` date NOT NULL,
  `waktu` time NOT NULL DEFAULT '00:00:00',
  `id_lampu` varchar(10) NOT NULL,
  `status` varchar(11) NOT NULL,
  `asal` varchar(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log`
--

LOCK TABLES `log` WRITE;
/*!40000 ALTER TABLE `log` DISABLE KEYS */;
INSERT INTO `log` VALUES ('2012-12-25','19:00:00','1','on','penjadwalan'),('2012-12-25','19:05:00','1','off','penjadwalan'),('2012-12-26','13:01:03','2','on','Twitter'),('2012-12-26','18:04:26','1','on','saklar'),('2012-12-26','18:05:08','1','off','saklar'),('2012-12-27','06:59:54','1','on','saklar'),('2012-12-27','07:00:27','1','off','saklar'),('2012-12-27','07:02:56','1','on','saklar'),('2012-12-27','07:55:20','1','off','saklar'),('2012-12-27','07:55:57','1','on','Twitter'),('2012-12-27','07:57:29','1','on','saklar'),('2012-12-27','07:57:33','2','on','saklar'),('2012-12-27','07:58:27','1','off','Twitter'),('2012-12-27','08:14:58','1','off','saklar'),('2012-12-27','08:15:07','2','off','saklar'),('2012-12-28','16:35:53','1','on','saklar'),('2012-12-28','16:36:45','1','off','saklar'),('2012-12-28','17:18:00','2','on','penjadwalan'),('2012-12-28','17:18:00','2','on','penjadwalan'),('2012-12-28','17:18:00','1','on','penjadwalan'),('2012-12-28','17:27:00','1','on','penjadwalan'),('2012-12-28','17:28:00','1','off','penjadwalan'),('2013-01-01','23:32:02','1','on','saklar'),('2013-01-01','23:32:07','2','on','saklar'),('2013-01-01','23:38:37','1','on','Twitter'),('2013-01-01','23:38:39','2','on','Twitter'),('2013-01-03','17:18:00','2','on','penjadwalan'),('2013-01-03','17:29:00','2','on','penjadwalan'),('2013-01-03','17:29:00','1','on','penjadwalan');
/*!40000 ALTER TABLE `log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `penjadwalan`
--

DROP TABLE IF EXISTS `penjadwalan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `penjadwalan` (
  `id_lampu` char(3) NOT NULL DEFAULT '',
  `id_jadwal` char(3) NOT NULL DEFAULT '',
  `status_jadwal` char(10) DEFAULT NULL,
  PRIMARY KEY (`id_lampu`,`id_jadwal`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `penjadwalan`
--

LOCK TABLES `penjadwalan` WRITE;
/*!40000 ALTER TABLE `penjadwalan` DISABLE KEYS */;
/*!40000 ALTER TABLE `penjadwalan` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-01-03 19:27:55
