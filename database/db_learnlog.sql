-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 31, 2025 at 11:33 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_learnlog`
--

-- --------------------------------------------------------

--
-- Table structure for table `learning_entries`
--

DROP TABLE IF EXISTS `learning_entries`;
CREATE TABLE `learning_entries` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `title` varchar(200) NOT NULL,
  `content` text NOT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `project` varchar(255) DEFAULT NULL,
  `reflection` text DEFAULT NULL,
  `resources` text DEFAULT NULL,
  `time_spent` float DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `learning_entries`
--

INSERT INTO `learning_entries` (`id`, `date`, `title`, `content`, `tags`, `project`, `reflection`, `resources`, `time_spent`, `user_id`) VALUES
(5, '2025-07-30', 'Introduction to Data Structure', 'Learned about arrays, linked lists, and stacks. Practiced implementing them in C++.', 'Data Structures, C++, Algorithms', 'Semester Data Structures Lab', 'Strengthened my understanding of how data is organized in memory. Feeling more confident about solving problems efficiently.', 'Textbook Data Structures and Algorithms in C++, YouTube channel MyCodeSchool.', 3, 2);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password`) VALUES
(2, 'Shital', 'shitalpanhalkar10@gmail.com', 'scrypt:32768:8:1$LKgBP5qEsC7aalZP$0cba86fcdef20ad336684b716a018a456dcd170edf2a3f435cb82907be57a9423efdf53717d902f48204151dd1a72790f29b5c95125bae6976097041c229b300');

--
-- Set AUTO_INCREMENT values
--

ALTER TABLE `learning_entries` AUTO_INCREMENT = 6;
ALTER TABLE `users` AUTO_INCREMENT = 3;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
