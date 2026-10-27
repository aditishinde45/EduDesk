-- =============================================================================
-- K. K. Wagh Institute of Engineering Education & Research (Polytechnic), Nashik
-- Certificate Management System (EduDesk)
-- Database: PostgreSQL (for pgAdmin / Postgres.app)
-- Relational Schema: Tables 5.1 to 5.12 with PK, FK, Constraints, and Cascade/Restrict rules
-- =============================================================================

-- Drop views if exist
DROP VIEW IF EXISTS v_certificate_details CASCADE;
DROP VIEW IF EXISTS v_student_with_age CASCADE;

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS "Notification" CASCADE;
DROP TABLE IF EXISTS "Audit_Log" CASCADE;
DROP TABLE IF EXISTS "Revocation" CASCADE;
DROP TABLE IF EXISTS "Certificate" CASCADE;
DROP TABLE IF EXISTS "Users" CASCADE;
DROP TABLE IF EXISTS "Student_Phone" CASCADE;
DROP TABLE IF EXISTS "Student" CASCADE;
DROP TABLE IF EXISTS "Authority_Phone" CASCADE;
DROP TABLE IF EXISTS "Issuing_Authority" CASCADE;
DROP TABLE IF EXISTS "Certificate_Type" CASCADE;
DROP TABLE IF EXISTS "Course" CASCADE;
DROP TABLE IF EXISTS "Department" CASCADE;

-- -----------------------------------------------------------------------------
-- Table 5.1: Department
-- -----------------------------------------------------------------------------
CREATE TABLE "Department" (
    "Department_ID" SERIAL PRIMARY KEY,
    "Department_Name" VARCHAR(100) NOT NULL UNIQUE,
    "HOD_Name" VARCHAR(100),
    "Email" VARCHAR(100) UNIQUE
);

CREATE INDEX idx_dept_name ON "Department" ("Department_Name");

-- -----------------------------------------------------------------------------
-- Table 5.2: Course
-- Foreign Key: Department_ID -> Department (ON DELETE RESTRICT, ON UPDATE CASCADE)
-- -----------------------------------------------------------------------------
CREATE TABLE "Course" (
    "Course_ID" SERIAL PRIMARY KEY,
    "Course_Name" VARCHAR(100) NOT NULL,
    "Duration" VARCHAR(30),
    "Department_ID" INT NOT NULL,
    CONSTRAINT fk_course_department
        FOREIGN KEY ("Department_ID")
        REFERENCES "Department"("Department_ID")
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE INDEX idx_course_dept ON "Course" ("Department_ID");

-- -----------------------------------------------------------------------------
-- Table 5.3: Certificate_Type
-- -----------------------------------------------------------------------------
CREATE TABLE "Certificate_Type" (
    "Type_ID" SERIAL PRIMARY KEY,
    "Type_Name" VARCHAR(50) NOT NULL UNIQUE,
    "Description" VARCHAR(255)
);

-- -----------------------------------------------------------------------------
-- Table 5.4: Issuing_Authority
-- -----------------------------------------------------------------------------
CREATE TABLE "Issuing_Authority" (
    "Authority_ID" SERIAL PRIMARY KEY,
    "Authority_Name" VARCHAR(100) NOT NULL,
    "Registration_No" VARCHAR(50) UNIQUE,
    "Email" VARCHAR(100),
    "Website" VARCHAR(150),
    "House_no" VARCHAR(20),
    "Street" VARCHAR(100),
    "City" VARCHAR(50),
    "State" VARCHAR(50),
    "Pincode" CHAR(6)
);

-- -----------------------------------------------------------------------------
-- Table 5.5: Authority_Phone (Multivalued Attribute)
-- Composite Primary Key = (Authority_ID, Phone_No)
-- Foreign Key: Authority_ID -> Issuing_Authority (ON DELETE CASCADE, ON UPDATE CASCADE)
-- -----------------------------------------------------------------------------
CREATE TABLE "Authority_Phone" (
    "Authority_ID" INT NOT NULL,
    "Phone_No" VARCHAR(15) NOT NULL,
    PRIMARY KEY ("Authority_ID", "Phone_No"),
    CONSTRAINT fk_auth_phone_authority
        FOREIGN KEY ("Authority_ID")
        REFERENCES "Issuing_Authority"("Authority_ID")
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- -----------------------------------------------------------------------------
-- Table 5.6: Student
-- Age is a DERIVED attribute: calculated from Date_of_Birth in views/queries.
-- Foreign Keys:
--   Department_ID -> Department (ON DELETE RESTRICT, ON UPDATE CASCADE)
--   Course_ID -> Course (ON DELETE RESTRICT, ON UPDATE CASCADE)
-- -----------------------------------------------------------------------------
CREATE TABLE "Student" (
    "Student_ID" SERIAL PRIMARY KEY,
    "First_Name" VARCHAR(50) NOT NULL,
    "Last_Name" VARCHAR(50),
    "Email" VARCHAR(100) UNIQUE,
    "Enrollment_No" VARCHAR(30) NOT NULL UNIQUE,
    "Date_of_Birth" DATE,
    "Batch_Year" INT,
    "House_no" VARCHAR(20),
    "Street" VARCHAR(100),
    "City" VARCHAR(50),
    "State" VARCHAR(50),
    "Pincode" CHAR(6),
    "Department_ID" INT NOT NULL,
    "Course_ID" INT NOT NULL,
    CONSTRAINT fk_student_department
        FOREIGN KEY ("Department_ID")
        REFERENCES "Department"("Department_ID")
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_student_course
        FOREIGN KEY ("Course_ID")
        REFERENCES "Course"("Course_ID")
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE INDEX idx_student_enrollment ON "Student" ("Enrollment_No");
CREATE INDEX idx_student_dept ON "Student" ("Department_ID");
CREATE INDEX idx_student_course ON "Student" ("Course_ID");

-- -----------------------------------------------------------------------------
-- Table 5.7: Student_Phone (Multivalued Attribute)
-- Composite Primary Key = (Student_ID, Phone_No)
-- Foreign Key: Student_ID -> Student (ON DELETE CASCADE, ON UPDATE CASCADE)
-- -----------------------------------------------------------------------------
CREATE TABLE "Student_Phone" (
    "Student_ID" INT NOT NULL,
    "Phone_No" VARCHAR(15) NOT NULL,
    PRIMARY KEY ("Student_ID", "Phone_No"),
    CONSTRAINT fk_student_phone_student
        FOREIGN KEY ("Student_ID")
        REFERENCES "Student"("Student_ID")
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- -----------------------------------------------------------------------------
-- Table 5.8: Users
-- Role: Admin, Staff, Student
-- Student_ID nullable link for 1:1 student-user account isolation
-- -----------------------------------------------------------------------------
CREATE TABLE "Users" (
    "User_ID" SERIAL PRIMARY KEY,
    "Username" VARCHAR(50) NOT NULL UNIQUE,
    "Password_Hash" VARCHAR(255) NOT NULL,
    "Role" VARCHAR(20) NOT NULL CHECK ("Role" IN ('Admin', 'Staff', 'Student')),
    "Email" VARCHAR(100) UNIQUE,
    "Last_Login" TIMESTAMP NULL,
    "Student_ID" INT UNIQUE,
    CONSTRAINT fk_users_student
        FOREIGN KEY ("Student_ID")
        REFERENCES "Student"("Student_ID")
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE INDEX idx_users_username ON "Users" ("Username");

-- -----------------------------------------------------------------------------
-- Table 5.9: Certificate
-- Status: 'Active', 'Expired', 'Revoked'
-- Foreign Keys:
--   Student_ID -> Student (ON DELETE RESTRICT, ON UPDATE CASCADE)
--   Type_ID -> Certificate_Type (ON DELETE RESTRICT, ON UPDATE CASCADE)
--   Authority_ID -> Issuing_Authority (ON DELETE RESTRICT, ON UPDATE CASCADE)
-- -----------------------------------------------------------------------------
CREATE TABLE "Certificate" (
    "Certificate_ID" SERIAL PRIMARY KEY,
    "Certificate_Number" VARCHAR(30) NOT NULL UNIQUE,
    "Certificate_Name" VARCHAR(150) NOT NULL,
    "Issue_Date" DATE NOT NULL,
    "Expiry_Date" DATE NULL,
    "Status" VARCHAR(10) DEFAULT 'Active' CHECK ("Status" IN ('Active', 'Expired', 'Revoked')),
    "Grade" VARCHAR(10),
    "QR_Code" VARCHAR(255),
    "Certificate_File" VARCHAR(255),
    "Student_ID" INT NOT NULL,
    "Type_ID" INT NOT NULL,
    "Authority_ID" INT NOT NULL,
    CONSTRAINT fk_cert_student
        FOREIGN KEY ("Student_ID")
        REFERENCES "Student"("Student_ID")
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_cert_type
        FOREIGN KEY ("Type_ID")
        REFERENCES "Certificate_Type"("Type_ID")
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_cert_authority
        FOREIGN KEY ("Authority_ID")
        REFERENCES "Issuing_Authority"("Authority_ID")
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE INDEX idx_cert_number ON "Certificate" ("Certificate_Number");
CREATE INDEX idx_cert_student ON "Certificate" ("Student_ID");
CREATE INDEX idx_cert_status ON "Certificate" ("Status");

-- -----------------------------------------------------------------------------
-- Table 5.10: Revocation (WEAK Entity)
-- Identifying relationship: Certificate - Has_Revocation - Revocation
-- Composite Primary Key = (Certificate_ID, Revocation_No)
-- Foreign Keys:
--   Certificate_ID -> Certificate (ON DELETE CASCADE, ON UPDATE CASCADE)
--   User_ID -> Users (ON DELETE RESTRICT, ON UPDATE CASCADE)
-- -----------------------------------------------------------------------------
CREATE TABLE "Revocation" (
    "Certificate_ID" INT NOT NULL,
    "Revocation_No" INT NOT NULL,
    "Reason" VARCHAR(255) NOT NULL,
    "Revoked_Date" DATE NOT NULL,
    "User_ID" INT NOT NULL,
    PRIMARY KEY ("Certificate_ID", "Revocation_No"),
    CONSTRAINT fk_revocation_certificate
        FOREIGN KEY ("Certificate_ID")
        REFERENCES "Certificate"("Certificate_ID")
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_revocation_user
        FOREIGN KEY ("User_ID")
        REFERENCES "Users"("User_ID")
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- -----------------------------------------------------------------------------
-- Table 5.11: Audit_Log
-- Foreign Key: User_ID -> Users (ON DELETE RESTRICT, ON UPDATE CASCADE)
-- -----------------------------------------------------------------------------
CREATE TABLE "Audit_Log" (
    "Log_ID" SERIAL PRIMARY KEY,
    "Action" VARCHAR(100) NOT NULL,
    "Timestamp" TIMESTAMP NOT NULL,
    "IP_Address" VARCHAR(45),
    "User_ID" INT NOT NULL,
    CONSTRAINT fk_audit_user
        FOREIGN KEY ("User_ID")
        REFERENCES "Users"("User_ID")
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE INDEX idx_audit_timestamp ON "Audit_Log" ("Timestamp");

-- -----------------------------------------------------------------------------
-- Table 5.12: Notification
-- Foreign Key: User_ID -> Users (ON DELETE CASCADE, ON UPDATE CASCADE)
-- -----------------------------------------------------------------------------
CREATE TABLE "Notification" (
    "Notification_ID" SERIAL PRIMARY KEY,
    "Message" TEXT NOT NULL,
    "Sent_Date" TIMESTAMP NOT NULL,
    "Status" VARCHAR(15) DEFAULT 'Unread',
    "User_ID" INT NOT NULL,
    CONSTRAINT fk_notification_user
        FOREIGN KEY ("User_ID")
        REFERENCES "Users"("User_ID")
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE INDEX idx_notif_user ON "Notification" ("User_ID");

-- -----------------------------------------------------------------------------
-- Derived View: Student with calculated Age
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_student_with_age AS
SELECT 
    s."Student_ID",
    s."First_Name",
    s."Last_Name",
    CONCAT(s."First_Name", ' ', COALESCE(s."Last_Name", '')) AS "Full_Name",
    s."Email",
    s."Enrollment_No",
    s."Date_of_Birth",
    CASE 
        WHEN s."Date_of_Birth" IS NOT NULL THEN
            EXTRACT(YEAR FROM age(CURRENT_DATE, s."Date_of_Birth"))::INT
        ELSE NULL
    END AS "Calculated_Age",
    s."Batch_Year",
    s."Department_ID",
    d."Department_Name",
    s."Course_ID",
    c."Course_Name"
FROM "Student" s
JOIN "Department" d ON s."Department_ID" = d."Department_ID"
JOIN "Course" c ON s."Course_ID" = c."Course_ID";

-- -----------------------------------------------------------------------------
-- Derived View: Certificate Details
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_certificate_details AS
SELECT 
    c."Certificate_ID",
    c."Certificate_Number",
    c."Certificate_Name",
    c."Issue_Date",
    c."Expiry_Date",
    c."Status",
    c."Grade",
    c."QR_Code",
    s."Enrollment_No",
    CONCAT(s."First_Name", ' ', COALESCE(s."Last_Name", '')) AS "Student_Name",
    t."Type_Name",
    a."Authority_Name"
FROM "Certificate" c
JOIN "Student" s ON c."Student_ID" = s."Student_ID"
JOIN "Certificate_Type" t ON c."Type_ID" = t."Type_ID"
JOIN "Issuing_Authority" a ON c."Authority_ID" = a."Authority_ID";

-- -----------------------------------------------------------------------------
-- Unquoted / Lowercase Aliases for convenient queries in pgAdmin / SQL
-- Allows querying `SELECT * FROM student;` or `SELECT * FROM "Student";`
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW department AS SELECT * FROM "Department";
CREATE OR REPLACE VIEW course AS SELECT * FROM "Course";
CREATE OR REPLACE VIEW student AS SELECT * FROM "Student";
CREATE OR REPLACE VIEW certificate AS SELECT * FROM "Certificate";
CREATE OR REPLACE VIEW users AS SELECT * FROM "Users";
CREATE OR REPLACE VIEW revocation AS SELECT * FROM "Revocation";
CREATE OR REPLACE VIEW certificate_type AS SELECT * FROM "Certificate_Type";
CREATE OR REPLACE VIEW issuing_authority AS SELECT * FROM "Issuing_Authority";
CREATE OR REPLACE VIEW audit_log AS SELECT * FROM "Audit_Log";
CREATE OR REPLACE VIEW notification AS SELECT * FROM "Notification";
CREATE OR REPLACE VIEW student_phone AS SELECT * FROM "Student_Phone";
CREATE OR REPLACE VIEW authority_phone AS SELECT * FROM "Authority_Phone";

-- Grant full privileges to postgres and public
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

