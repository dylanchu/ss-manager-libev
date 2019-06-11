-- MySQL dump 10.16  Distrib 10.1.33-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: ssman1
-- ------------------------------------------------------
-- Server version	10.1.32-MariaDB

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
-- Table structure for table `ss_traffic`
--

DROP TABLE IF EXISTS `ss_traffic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ss_traffic` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `uid` int(10) unsigned DEFAULT NULL,
  `ss_port` int(6) unsigned NOT NULL,
  `log_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `traffic` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `uid` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `note` varchar(256) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) CHARACTER SET utf8mb4 NOT NULL,
  `level` smallint(6) NOT NULL DEFAULT '0',
  `email` varchar(32) NOT NULL,
  `password` varchar(48) NOT NULL,
  `ss_port` int(11) NOT NULL,
  `ss_pwd` varchar(16) NOT NULL,
  `ss_enabled` tinyint(1) NOT NULL DEFAULT '1',
  `ss_method` varchar(32) NOT NULL DEFAULT 'aes-128-cfb',
  `traffic_up` bigint(20) NOT NULL DEFAULT '0',
  `traffic_down` bigint(20) NOT NULL DEFAULT '0',
  `traffic_quota` bigint(20) NOT NULL DEFAULT '0',
  `last_use_time` datetime NOT NULL DEFAULT '1999-01-01 08:00:00',
  `plan_type` varchar(32) NOT NULL DEFAULT 'free',
  `plan_end_time` datetime NOT NULL DEFAULT '2099-12-31 12:00:00',
  `total_paid` int(11) NOT NULL DEFAULT '0',
  `last_gift_time` datetime NOT NULL DEFAULT '1999-01-01 08:00:00',
  `last_check_in_time` datetime NOT NULL DEFAULT '1999-01-01 08:00:00',
  `last_reset_pwd_time` datetime NOT NULL DEFAULT '1999-01-01 08:00:00',
  `reg_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `reg_ip` char(39) NOT NULL DEFAULT '127.0.0.1',
  `referee` int(11) NOT NULL DEFAULT '0',
  `invite_num` smallint(6) NOT NULL DEFAULT '0',
  `email_verified` tinyint(1) NOT NULL DEFAULT '0',
  `protocol` char(32) NOT NULL DEFAULT 'origin',
  `obfs` char(32) NOT NULL DEFAULT 'plain',
  `type` smallint(6) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `port` (`ss_port`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

-- Dump completed on 2018-05-21 15:45:20
