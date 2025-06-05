-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: banco_malvader
-- ------------------------------------------------------
-- Server version	8.0.42

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
-- Table structure for table `auditoria`
--

DROP TABLE IF EXISTS `auditoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auditoria` (
  `id_auditoria` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int DEFAULT NULL,
  `acao` varchar(50) NOT NULL,
  `data_hora` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `detalhes` text,
  PRIMARY KEY (`id_auditoria`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `auditoria_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `conta`
--

DROP TABLE IF EXISTS `conta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `conta` (
  `id_conta` int NOT NULL AUTO_INCREMENT,
  `numero_conta` varchar(10) NOT NULL,
  `tipo` enum('CC','CP','CI') NOT NULL,
  `saldo` decimal(10,2) DEFAULT '0.00',
  `data_abertura` datetime DEFAULT CURRENT_TIMESTAMP,
  `id_cliente` int NOT NULL,
  `id_funcionario` int NOT NULL,
  `ativa` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id_conta`),
  UNIQUE KEY `numero_conta` (`numero_conta`),
  KEY `id_cliente` (`id_cliente`),
  KEY `id_funcionario` (`id_funcionario`),
  CONSTRAINT `conta_ibfk_1` FOREIGN KEY (`id_cliente`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `conta_ibfk_2` FOREIGN KEY (`id_funcionario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `historico_encerramento`
--

DROP TABLE IF EXISTS `historico_encerramento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historico_encerramento` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_conta` int NOT NULL,
  `id_funcionario` int NOT NULL,
  `motivo` text NOT NULL,
  `data_encerramento` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `id_conta` (`id_conta`),
  KEY `id_funcionario` (`id_funcionario`),
  CONSTRAINT `historico_encerramento_ibfk_1` FOREIGN KEY (`id_conta`) REFERENCES `conta` (`id_conta`),
  CONSTRAINT `historico_encerramento_ibfk_2` FOREIGN KEY (`id_funcionario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `movimentacao`
--

DROP TABLE IF EXISTS `movimentacao`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimentacao` (
  `id_movimentacao` int NOT NULL AUTO_INCREMENT,
  `id_conta` int NOT NULL,
  `tipo` enum('DEPOSITO','SAQUE','TRANSFERENCIA') DEFAULT NULL,
  `valor` decimal(10,2) DEFAULT NULL,
  `data_movimentacao` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_movimentacao`),
  KEY `id_conta` (`id_conta`),
  CONSTRAINT `movimentacao_ibfk_1` FOREIGN KEY (`id_conta`) REFERENCES `conta` (`id_conta`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `cpf` varchar(11) NOT NULL,
  `data_nascimento` date NOT NULL,
  `telefone` varchar(15) NOT NULL,
  `tipo_usuario` enum('FUNCIONARIO','CLIENTE') NOT NULL,
  `senha_hash` varchar(32) NOT NULL,
  `otp_ativo` varchar(6) DEFAULT NULL,
  `otp_expiracao` datetime DEFAULT NULL,
  `tentativas_login` int DEFAULT '0',
  `bloqueado_ate` datetime DEFAULT NULL,
  `eh_gerente` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `cpf` (`cpf`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `view_clientes`
--

DROP TABLE IF EXISTS `view_clientes`;
/*!50001 DROP VIEW IF EXISTS `view_clientes`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_clientes` AS SELECT 
 1 AS `id_usuario`,
 1 AS `nome`,
 1 AS `cpf`,
 1 AS `telefone`,
 1 AS `saldo_total`,
 1 AS `score_credito`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_contas_ativas`
--

DROP TABLE IF EXISTS `view_contas_ativas`;
/*!50001 DROP VIEW IF EXISTS `view_contas_ativas`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_contas_ativas` AS SELECT 
 1 AS `id_conta`,
 1 AS `numero_conta`,
 1 AS `tipo`,
 1 AS `saldo`,
 1 AS `nome_cliente`,
 1 AS `data_abertura`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_desempenho_func`
--

DROP TABLE IF EXISTS `view_desempenho_func`;
/*!50001 DROP VIEW IF EXISTS `view_desempenho_func`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_desempenho_func` AS SELECT 
 1 AS `id_usuario`,
 1 AS `nome`,
 1 AS `contas_criadas`,
 1 AS `contas_ativas`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_funcionarios`
--

DROP TABLE IF EXISTS `view_funcionarios`;
/*!50001 DROP VIEW IF EXISTS `view_funcionarios`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_funcionarios` AS SELECT 
 1 AS `id_usuario`,
 1 AS `nome`,
 1 AS `cpf`,
 1 AS `telefone`,
 1 AS `contas_abertas`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_inadimplencia`
--

DROP TABLE IF EXISTS `view_inadimplencia`;
/*!50001 DROP VIEW IF EXISTS `view_inadimplencia`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_inadimplencia` AS SELECT 
 1 AS `id_conta`,
 1 AS `numero_conta`,
 1 AS `titular`,
 1 AS `saldo`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `view_movimentacoes`
--

DROP TABLE IF EXISTS `view_movimentacoes`;
/*!50001 DROP VIEW IF EXISTS `view_movimentacoes`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_movimentacoes` AS SELECT 
 1 AS `id_movimentacao`,
 1 AS `tipo`,
 1 AS `valor`,
 1 AS `data_movimentacao`,
 1 AS `numero_conta`,
 1 AS `titular`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `view_clientes`
--

/*!50001 DROP VIEW IF EXISTS `view_clientes`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_clientes` AS select `u`.`id_usuario` AS `id_usuario`,`u`.`nome` AS `nome`,`u`.`cpf` AS `cpf`,`u`.`telefone` AS `telefone`,coalesce(sum(`c`.`saldo`),0) AS `saldo_total`,round((coalesce(sum(`c`.`saldo`),0) * 0.05),2) AS `score_credito` from (`usuario` `u` left join `conta` `c` on(((`c`.`id_cliente` = `u`.`id_usuario`) and (`c`.`ativa` = true)))) where (`u`.`tipo_usuario` = 'CLIENTE') group by `u`.`id_usuario` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_contas_ativas`
--

/*!50001 DROP VIEW IF EXISTS `view_contas_ativas`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_contas_ativas` AS select `c`.`id_conta` AS `id_conta`,`c`.`numero_conta` AS `numero_conta`,`c`.`tipo` AS `tipo`,`c`.`saldo` AS `saldo`,`u`.`nome` AS `nome_cliente`,`c`.`data_abertura` AS `data_abertura` from (`conta` `c` join `usuario` `u` on((`c`.`id_cliente` = `u`.`id_usuario`))) where (`c`.`ativa` = true) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_desempenho_func`
--

/*!50001 DROP VIEW IF EXISTS `view_desempenho_func`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_desempenho_func` AS select `u`.`id_usuario` AS `id_usuario`,`u`.`nome` AS `nome`,count(`c`.`id_conta`) AS `contas_criadas`,sum((case when `c`.`ativa` then 1 else 0 end)) AS `contas_ativas` from (`usuario` `u` left join `conta` `c` on((`c`.`id_funcionario` = `u`.`id_usuario`))) where (`u`.`tipo_usuario` = 'FUNCIONARIO') group by `u`.`id_usuario` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_funcionarios`
--

/*!50001 DROP VIEW IF EXISTS `view_funcionarios`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_funcionarios` AS select `u`.`id_usuario` AS `id_usuario`,`u`.`nome` AS `nome`,`u`.`cpf` AS `cpf`,`u`.`telefone` AS `telefone`,count(`c`.`id_conta`) AS `contas_abertas` from (`usuario` `u` left join `conta` `c` on((`c`.`id_funcionario` = `u`.`id_usuario`))) where (`u`.`tipo_usuario` = 'FUNCIONARIO') group by `u`.`id_usuario` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_inadimplencia`
--

/*!50001 DROP VIEW IF EXISTS `view_inadimplencia`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_inadimplencia` AS select `c`.`id_conta` AS `id_conta`,`c`.`numero_conta` AS `numero_conta`,`u`.`nome` AS `titular`,`c`.`saldo` AS `saldo` from (`conta` `c` join `usuario` `u` on((`c`.`id_cliente` = `u`.`id_usuario`))) where (`c`.`saldo` < 0) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `view_movimentacoes`
--

/*!50001 DROP VIEW IF EXISTS `view_movimentacoes`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_movimentacoes` AS select `m`.`id_movimentacao` AS `id_movimentacao`,`m`.`tipo` AS `tipo`,`m`.`valor` AS `valor`,`m`.`data_movimentacao` AS `data_movimentacao`,`c`.`numero_conta` AS `numero_conta`,`u`.`nome` AS `titular` from ((`movimentacao` `m` join `conta` `c` on((`m`.`id_conta` = `c`.`id_conta`))) join `usuario` `u` on((`c`.`id_cliente` = `u`.`id_usuario`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-04 22:04:38
