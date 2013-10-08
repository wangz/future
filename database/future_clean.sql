-- MySQL dump 10.13  Distrib 5.1.69, for redhat-linux-gnu (x86_64)
--
-- Host: localhost    Database: future2
-- ------------------------------------------------------
-- Server version	5.1.69

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
-- Table structure for table `data_buy`
--

DROP TABLE IF EXISTS `data_buy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data_buy` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `origin` varchar(45) NOT NULL,
  `contract` varchar(45) NOT NULL,
  `company` varchar(45) NOT NULL,
  `value_type` varchar(45) NOT NULL,
  `real_value` int(11) NOT NULL,
  `pub_date` varchar(45) NOT NULL,
  `real_get_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7155 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `data_buy`
--

LOCK TABLES `data_buy` WRITE;
/*!40000 ALTER TABLE `data_buy` DISABLE KEYS */;
/*!40000 ALTER TABLE `data_buy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `data_selling`
--

DROP TABLE IF EXISTS `data_selling`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data_selling` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `origin` varchar(45) NOT NULL,
  `contract` varchar(45) NOT NULL,
  `company` varchar(45) NOT NULL,
  `value_type` varchar(45) NOT NULL,
  `real_value` int(11) NOT NULL,
  `pub_date` varchar(45) NOT NULL,
  `real_get_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6475 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `data_selling`
--

LOCK TABLES `data_selling` WRITE;
/*!40000 ALTER TABLE `data_selling` DISABLE KEYS */;
/*!40000 ALTER TABLE `data_selling` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `data_trading`
--

DROP TABLE IF EXISTS `data_trading`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data_trading` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `origin` varchar(45) NOT NULL,
  `contract` varchar(45) NOT NULL,
  `company` varchar(45) NOT NULL,
  `value_type` varchar(45) NOT NULL,
  `real_value` int(11) NOT NULL,
  `pub_date` varchar(45) NOT NULL,
  `real_get_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6557 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `data_trading`
--

LOCK TABLES `data_trading` WRITE;
/*!40000 ALTER TABLE `data_trading` DISABLE KEYS */;
/*!40000 ALTER TABLE `data_trading` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-10-08 11:00:19
