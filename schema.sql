-- =============================================================================
-- K. K. Wagh Institute of Engineering Education & Research (Polytechnic), Nashik
-- Certificate Management System (EduDesk)
-- Database: MySQL
-- Relational Schema: Tables 5.1 to 5.12 with PK, FK, Constraints, and Cascade/Restrict rules
-- =============================================================================

CREATE DATABASE IF NOT EXISTS edudesk_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE edudesk_db;

-- Disable FK checks temporarily for safe clean recreation
SET FOREIGN_KEY_CHECKS = 0;

DROP VIEW IF EXISTS v_student_with_age;
DROP VIEW IF EXISTS v_certificate_details;
DROP TABLE IF EXISTS Notification;
DROP TABLE IF EXISTS Audit_Log;
DROP TABLE IF EXISTS Revocation;
DROP TABLE IF EXISTS Certificate;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Student_Phone;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS Authority_Phone;
DROP TABLE IF EXISTS Issuing_Authority;
DROP TABLE IF EXISTS Certificate_Type;
DROP TABLE IF EXISTS Course;
DROP TABLE IF EXISTS Department;

SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- Table 5.1: Department
-- -----------------------------------------------------------------------------
CREATE TABLE Department (
    Department_ID INT AUTO_INCREMENT PRIMARY KEY,
    Department_Name VARCHAR(100) NOT NULL UNIQUE,
    HOD_Name VARCHAR(100),
    Email VARCHAR(100) UNIQUE,
    INDEX idx_dept_name (Department_Name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 5.2: Course
-- Foreign Key: Department_ID -> Department (ON DELETE RESTRICT, ON UPDATE CASCADE)
-- -----------------------------------------------------------------------------
CREATE TABLE Course (
    Course_ID INT AUTO_INCREMENT PRIMARY KEY,
    Course_Name VARCHAR(100) NOT NULL,
    Duration VARCHAR(30),
    Department_ID INT NOT NULL,
    CONSTRAINT fk_course_department
        FOREIGN KEY (Department_ID)
        REFERENCES Department(Department_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX idx_course_dept (Department_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 5.3: Certificate_Type
-- -----------------------------------------------------------------------------
CREATE TABLE Certificate_Type (
    Type_ID INT AUTO_INCREMENT PRIMARY KEY,
    Type_Name VARCHAR(50) NOT NULL UNIQUE,
    Description VARCHAR(255),
    INDEX idx_type_name (Type_Name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 5.4: Issuing_Authority
-- -----------------------------------------------------------------------------
CREATE TABLE Issuing_Authority (
    Authority_ID INT AUTO_INCREMENT PRIMARY KEY,
    Authority_Name VARCHAR(100) NOT NULL,
    Registration_No VARCHAR(50) UNIQUE,
    Email VARCHAR(100),
    Website VARCHAR(150),
    House_no VARCHAR(20),
    Street VARCHAR(100),
    City VARCHAR(50),
    State VARCHAR(50),
    Pincode CHAR(6),
    INDEX idx_auth_name (Authority_Name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 5.5: Authority_Phone (Multivalued Attribute)
-- Foreign Key: Authority_ID -> Issuing_Authority (ON DELETE CASCADE, ON UPDATE CASCADE)
-- Primary Key: (Authority_ID, Phone_No)
-- -----------------------------------------------------------------------------
CREATE TABLE Authority_Phone (
    Authority_ID INT NOT NULL,
    Phone_No VARCHAR(15) NOT NULL,
    PRIMARY KEY (Authority_ID, Phone_No),
    CONSTRAINT fk_authphone_authority
        FOREIGN KEY (Authority_ID)
        REFERENCES Issuing_Authority(Authority_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 5.6: Student
-- Foreign Keys: Department_ID, Course_ID -> RESTRICT / CASCADE
-- Note: Age is a DERIVED attribute (computed from Date_of_Birth, NOT stored)
-- -----------------------------------------------------------------------------
CREATE TABLE Student (
    Student_ID INT AUTO_INCREMENT PRIMARY KEY,
    First_Name VARCHAR(50) NOT NULL,
    Last_Name VARCHAR(50),
    Email VARCHAR(100) UNIQUE,
    Enrollment_No VARCHAR(30) NOT NULL UNIQUE,
    Date_of_Birth DATE,
    Batch_Year INT,
    House_no VARCHAR(20),
    Street VARCHAR(100),
    City VARCHAR(50),
    State VARCHAR(50),
    Pincode CHAR(6),
    Department_ID INT NOT NULL,
    Course_ID INT NOT NULL,
    CONSTRAINT fk_student_department
        FOREIGN KEY (Department_ID)
        REFERENCES Department(Department_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_student_course
        FOREIGN KEY (Course_ID)
        REFERENCES Course(Course_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX idx_student_enrollment (Enrollment_No),
    INDEX idx_student_dept (Department_ID),
    INDEX idx_student_course (Course_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 5.7: Student_Phone (Multivalued Attribute)
-- Foreign Key: Student_ID -> Student (ON DELETE CASCADE, ON UPDATE CASCADE)
-- Primary Key: (Student_ID, Phone_No)
-- -----------------------------------------------------------------------------
CREATE TABLE Student_Phone (
    Student_ID INT NOT NULL,
    Phone_No VARCHAR(15) NOT NULL,
    PRIMARY KEY (Student_ID, Phone_No),
    CONSTRAINT fk_studphone_student
        FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 5.8: Users
-- Named "Users" because USER is a reserved word
-- Includes nullable Student_ID for direct student user account linkage
-- -----------------------------------------------------------------------------
CREATE TABLE Users (
    User_ID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Password_Hash VARCHAR(255) NOT NULL,
    Role VARCHAR(20) NOT NULL,
    Email VARCHAR(100) UNIQUE,
    Last_Login DATETIME NULL,
    Student_ID INT NULL,
    CONSTRAINT chk_user_role CHECK (Role IN ('Admin', 'Staff', 'Student')),
    CONSTRAINT fk_users_student
        FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    INDEX idx_users_username (Username),
    INDEX idx_users_role (Role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 5.9: Certificate
-- Foreign Keys: Student_ID, Type_ID, Authority_ID (ON DELETE RESTRICT, ON UPDATE CASCADE)
-- Check Constraint: Status in ('Active', 'Expired', 'Revoked')
-- -----------------------------------------------------------------------------
CREATE TABLE Certificate (
    Certificate_ID INT AUTO_INCREMENT PRIMARY KEY,
    Certificate_Number VARCHAR(30) NOT NULL UNIQUE,
    Certificate_Name VARCHAR(150) NOT NULL,
    Issue_Date DATE NOT NULL,
    Expiry_Date DATE NULL,
    Status VARCHAR(10) DEFAULT 'Active',
    Grade VARCHAR(10),
    QR_Code VARCHAR(255),
    Certificate_File VARCHAR(255),
    Student_ID INT NOT NULL,
    Type_ID INT NOT NULL,
    Authority_ID INT NOT NULL,
    CONSTRAINT chk_cert_status CHECK (Status IN ('Active', 'Expired', 'Revoked')),
    CONSTRAINT fk_cert_student
        FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_cert_type
        FOREIGN KEY (Type_ID)
        REFERENCES Certificate_Type(Type_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_cert_authority
        FOREIGN KEY (Authority_ID)
        REFERENCES Issuing_Authority(Authority_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX idx_cert_number (Certificate_Number),
    INDEX idx_cert_student (Student_ID),
    INDEX idx_cert_status (Status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 5.10: Revocation (WEAK Entity)
-- Primary Key: (Certificate_ID, Revocation_No)
-- Foreign Key: Certificate_ID -> Certificate (ON DELETE CASCADE, ON UPDATE CASCADE)
-- Foreign Key: User_ID -> Users (ON DELETE RESTRICT, ON UPDATE CASCADE)
-- -----------------------------------------------------------------------------
CREATE TABLE Revocation (
    Certificate_ID INT NOT NULL,
    Revocation_No INT NOT NULL,
    Reason VARCHAR(255) NOT NULL,
    Revoked_Date DATE NOT NULL,
    User_ID INT NOT NULL,
    PRIMARY KEY (Certificate_ID, Revocation_No),
    CONSTRAINT fk_revocation_certificate
        FOREIGN KEY (Certificate_ID)
        REFERENCES Certificate(Certificate_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_revocation_user
        FOREIGN KEY (User_ID)
        REFERENCES Users(User_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX idx_revocation_date (Revoked_Date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 5.11: Audit_Log
-- Foreign Key: User_ID -> Users (ON DELETE RESTRICT, ON UPDATE CASCADE)
-- -----------------------------------------------------------------------------
CREATE TABLE Audit_Log (
    Log_ID INT AUTO_INCREMENT PRIMARY KEY,
    Action VARCHAR(100) NOT NULL,
    Timestamp DATETIME NOT NULL,
    IP_Address VARCHAR(45),
    User_ID INT NOT NULL,
    CONSTRAINT fk_audit_user
        FOREIGN KEY (User_ID)
        REFERENCES Users(User_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX idx_audit_timestamp (Timestamp),
    INDEX idx_audit_action (Action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 5.12: Notification
-- Foreign Key: User_ID -> Users (ON DELETE CASCADE, ON UPDATE CASCADE)
-- -----------------------------------------------------------------------------
CREATE TABLE Notification (
    Notification_ID INT AUTO_INCREMENT PRIMARY KEY,
    Message TEXT NOT NULL,
    Sent_Date DATETIME NOT NULL,
    Status VARCHAR(15) DEFAULT 'Unread',
    User_ID INT NOT NULL,
    CONSTRAINT fk_notif_user
        FOREIGN KEY (User_ID)
        REFERENCES Users(User_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_notif_user (User_ID),
    INDEX idx_notif_status (Status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Views for Derived Attributes and Reporting
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_student_with_age AS
SELECT 
    s.Student_ID,
    s.First_Name,
    s.Last_Name,
    CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Full_Name,
    s.Email,
    s.Enrollment_No,
    s.Date_of_Birth,
    TIMESTAMPDIFF(YEAR, s.Date_of_Birth, CURDATE()) AS Age,
    s.Batch_Year,
    s.House_no,
    s.Street,
    s.City,
    s.State,
    s.Pincode,
    s.Department_ID,
    d.Department_Name,
    s.Course_ID,
    c.Course_Name
FROM Student s
JOIN Department d ON s.Department_ID = d.Department_ID
JOIN Course c ON s.Course_ID = c.Course_ID;

CREATE OR REPLACE VIEW v_certificate_details AS
SELECT 
    c.Certificate_ID,
    c.Certificate_Number,
    c.Certificate_Name,
    c.Issue_Date,
    c.Expiry_Date,
    c.Status,
    c.Grade,
    c.QR_Code,
    c.Certificate_File,
    s.Student_ID,
    CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
    s.Enrollment_No,
    d.Department_Name,
    co.Course_Name,
    ct.Type_Name AS Certificate_Type,
    ia.Authority_Name AS Issuing_Authority
FROM Certificate c
JOIN Student s ON c.Student_ID = s.Student_ID
JOIN Department d ON s.Department_ID = d.Department_ID
JOIN Course co ON s.Course_ID = co.Course_ID
JOIN Certificate_Type ct ON c.Type_ID = ct.Type_ID
JOIN Issuing_Authority ia ON c.Authority_ID = ia.Authority_ID;
