-- MySQL dump 10.16  Distrib 10.2.16-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: csv2
-- ------------------------------------------------------
-- Server version	10.2.16-MariaDB

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
-- Recreate test vms
--

LOCK TABLES `csv2_vms` WRITE;
/*!40000 ALTER TABLE `csv2_vms` DISABLE KEYS */;
DELETE FROM `csv2_vms` WHERE group_name = 'vm-test-group';
INSERT INTO `csv2_vms` VALUES
        ('vm-test-group','vm-test-cloud','vmid1','vm-test-authurl','vm-test-project','vm-test-group--vm-test-cloud--vmid1',0,'ACTIVE','5',NULL,1,0,0,NULL,1532955357,1532985482),
        ('vm-test-group','vm-test-cloud','vmid2','vm-test-authurl','vm-test-project','vm-test-group--vm-test-cloud--vmid2',0,'ACTIVE','4',NULL,1,0,0,NULL,1532979802,1532985482),
        ('vm-test-group','vm-test-cloud','vmid3','vm-test-authurl','vm-test-project','vm-test-group--vm-test-cloud--vmid3',0,'ACTIVE','4',NULL,1,0,0,NULL,1532980098,1532985482),
        ('vm-test-group','vm-test-cloud','vmid4','vm-test-authurl','vm-test-project','foreign-cloud--vmid4',0,'ACTIVE','4',NULL,1,0,0,NULL,1532980098,1532985482),
        ('vm-test-group','vm-test-cloud','vmid5','vm-test-authurl','vm-test-project','foreign-cloud--vmid5',0,'ACTIVE','4',NULL,1,0,0,NULL,1532980098,1532985482),
        ('vm-test-group','vm-test-cloud','vmid6','vm-test-authurl','vm-test-project','foreign-cloud--vmid6',0,'ACTIVE','4',NULL,1,0,0,NULL,1532980098,1532985482);
/*!40000 ALTER TABLE `csv2_vms` ENABLE KEYS */;
UNLOCK TABLES;
LOCK TABLES `condor_jobs` WRITE;
/*!40000 ALTER TABLE `condor_jobs` DISABLE KEYS */;
DELETE FROM `condor_jobs` WHERE group_name = 'vm-test-group';
INSERT INTO `condor_jobs` VALUES
        ('csv2-dev2.heprc.uvic.ca#1.0#1','vm-test-group',NULL,NULL,5,1,2000,15000000,NULL,5000000,'group_name is "vm-test-group"',10,1,0,'jodiew@csv2-dev2.heprc.uvic.ca',NULL,'vm-test-instance',NULL,0,NULL,NULL,NULL,1532028374,1532028374,NULL,'vm-testing');
/*!40000 ALTER TABLE `condor_jobs` ENABLE KEYS */;
UNLOCK TABLES;
LOCK TABLES `condor_machines` WRITE;
/*!40000 ALTER TABLE `condor_machines` DISABLE KEYS */;
DELETE FROM `condor_machines` WHERE group_name = 'vm-test-group';
INSERT INTO `condor_machines` VALUES
        ('vm-test-machine1','vm-test-group--vm-test-cloud--vmid1.ca','vm-test-group',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,NULL,NULL,'Partitionable',NULL,NULL,0,0),
        ('vm-test-machine2','vm-test-group--vm-test-cloud--vmid2.ca','vm-test-group',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,NULL,NULL,'Partitionable',NULL,NULL,0,0),
        ('vm-test-machine3','vm-test-group--vm-test-cloud--vmid3.ca','vm-test-group',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,NULL,NULL,'Partitionable',NULL,NULL,0,0);
/*!40000 ALTER TABLE `condor_machines` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-07-31 12:45:56
