-- ============================================================================
-- Dhrishti Study Point - Database Schema
-- Run this manually if you prefer to set up MySQL by hand instead of letting
-- Flask-SQLAlchemy auto-create tables on first run (db.create_all()).
--
-- Usage:
--   mysql -u root -p < schema.sql
-- ============================================================================

CREATE DATABASE IF NOT EXISTS dhrishti_study_point
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE dhrishti_study_point;

-- ------------------------------------------------------------------ admins
CREATE TABLE IF NOT EXISTS admins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(80) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------------- seats
CREATE TABLE IF NOT EXISTS seats (
  seat_no INT PRIMARY KEY,
  status VARCHAR(20) NOT NULL DEFAULT 'available'   -- 'available' | 'occupied'
) ENGINE=InnoDB;

-- ---------------------------------------------------------------- students
CREATE TABLE IF NOT EXISTS students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  mobile VARCHAR(15) NOT NULL,
  email VARCHAR(120),
  join_date DATE NOT NULL,
  seat_no INT,
  fee_status VARCHAR(20) NOT NULL DEFAULT 'Unpaid',  -- 'Paid' | 'Unpaid'
  fee_amount INT DEFAULT 900,
  fee_due_date DATE,
  is_active TINYINT(1) DEFAULT 1,
  FOREIGN KEY (seat_no) REFERENCES seats(seat_no)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -------------------------------------------------------------- attendance
CREATE TABLE IF NOT EXISTS attendance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  date DATE NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'Present',      -- 'Present' | 'Absent'
  FOREIGN KEY (student_id) REFERENCES students(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  UNIQUE KEY uix_student_date (student_id, date)
) ENGINE=InnoDB;

-- --------------------------------------------------------- contact_messages
CREATE TABLE IF NOT EXISTS contact_messages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  mobile VARCHAR(15),
  email VARCHAR(120),
  message TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_read TINYINT(1) DEFAULT 0
) ENGINE=InnoDB;

-- ------------------------------------------------------------- seed seats
-- Creates 40 seats numbered 1-40. Adjust the range if TOTAL_SEATS differs.
INSERT IGNORE INTO seats (seat_no, status)
SELECT n, 'available'
FROM (
  SELECT ROW_NUMBER() OVER () AS n
  FROM information_schema.columns
  LIMIT 40
) AS seq;
