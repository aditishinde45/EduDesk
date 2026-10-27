-- =============================================================================
-- K. K. Wagh Institute of Engineering Education & Research (Polytechnic), Nashik
-- Certificate Management System (EduDesk)
-- Standalone SQL Dummy Data Insert Script (for pgAdmin / PostgreSQL)
-- =============================================================================

-- 1. Departments
INSERT INTO "Department" ("Department_ID", "Department_Name", "HOD_Name", "Email") VALUES
(1, 'Computer Technology', 'Prof. P. B. Patil', 'hod_cm@kkwagh.edu.in'),
(2, 'Information Technology', 'Prof. S. M. Deshmukh', 'hod_it@kkwagh.edu.in'),
(3, 'Electronics & Telecommunication', 'Prof. V. K. Jadhav', 'hod_entc@kkwagh.edu.in'),
(4, 'Mechanical Engineering', 'Prof. R. D. Bhamare', 'hod_mech@kkwagh.edu.in'),
(5, 'Civil Engineering', 'Prof. N. S. Gaikwad', 'hod_civil@kkwagh.edu.in'),
(6, 'Artificial Intelligence & Data Science', 'Prof. A. R. Kulkarni', 'hod_aids@kkwagh.edu.in')
ON CONFLICT ("Department_ID") DO NOTHING;

SELECT setval(pg_get_serial_sequence('"Department"', 'Department_ID'), COALESCE(MAX("Department_ID"), 1)) FROM "Department";

-- 2. Courses
INSERT INTO "Course" ("Course_ID", "Course_Name", "Duration", "Department_ID") VALUES
(1, 'Diploma in Computer Technology', '3 Years', 1),
(2, 'Advance Diploma in AI & Machine Learning', '1 Year', 1),
(3, 'Diploma in Information Technology', '3 Years', 2),
(4, 'Diploma in Cloud Computing & Cybersecurity', '2 Years', 2),
(5, 'Diploma in Electronics & Telecommunication', '3 Years', 3),
(6, 'Diploma in VLSI & Embedded Systems', '1.5 Years', 3),
(7, 'Diploma in Mechanical Engineering', '3 Years', 4),
(8, 'Diploma in Mechatronics & Automation', '2 Years', 4),
(9, 'Diploma in Civil Engineering', '3 Years', 5),
(10, 'Diploma in AI & Data Science', '3 Years', 6)
ON CONFLICT ("Course_ID") DO NOTHING;

SELECT setval(pg_get_serial_sequence('"Course"', 'Course_ID'), COALESCE(MAX("Course_ID"), 1)) FROM "Course";

-- 3. Certificate Types
INSERT INTO "Certificate_Type" ("Type_ID", "Type_Name", "Description") VALUES
(1, 'Diploma Certificate', 'Official MSBTE Diploma completion credential awarded upon completing the academic curriculum.'),
(2, 'Merit Certificate', 'Awarded for academic excellence, departmental rank holders, and exceptional distinctions.'),
(3, 'Course Completion', 'Validating technical skill certifications and hands-on laboratory workshops.'),
(4, 'Project Excellence', 'Awarded for outstanding technical capstone projects, research, and engineering innovations.'),
(5, 'Industrial Internship', 'Validating completion of mandatory industrial in-plant internship and practical training.'),
(6, 'Technical Symposium Award', 'Recognizing excellence in national technical paper presentations and hackathons.')
ON CONFLICT ("Type_ID") DO NOTHING;

SELECT setval(pg_get_serial_sequence('"Certificate_Type"', 'Type_ID'), COALESCE(MAX("Type_ID"), 1)) FROM "Certificate_Type";

-- 4. Issuing Authorities
INSERT INTO "Issuing_Authority" ("Authority_ID", "Authority_Name", "Registration_No", "Email", "Website", "House_no", "Street", "City", "State", "Pincode") VALUES
(1, 'Maharashtra State Board of Technical Education (MSBTE)', 'MSBTE-MUM-1963', 'support@msbte.org.in', 'https://msbte.org.in', '49', 'Kherwadi, Ali Yawar Jung Marg, Bandra (E)', 'Mumbai', 'Maharashtra', '400051'),
(2, 'K. K. Wagh Polytechnic Examination Authority', 'KKW-POLY-EXAM-049', 'exam_cell@kkwagh.edu.in', 'https://poly.kkwagh.edu.in', 'Exam Cell Bldg', 'Hirabai Haridas Vidyanagari, Amrutdham', 'Nashik', 'Maharashtra', '422003'),
(3, 'Directorate of Technical Education (DTE), Maharashtra', 'DTE-MAH-1960', 'desk3@dtemaharashtra.gov.in', 'https://dtemaharashtra.gov.in', '3', 'Mahapalika Marg, Dhobi Talao', 'Mumbai', 'Maharashtra', '400001')
ON CONFLICT ("Authority_ID") DO NOTHING;

SELECT setval(pg_get_serial_sequence('"Issuing_Authority"', 'Authority_ID'), COALESCE(MAX("Authority_ID"), 1)) FROM "Issuing_Authority";

-- 5. Authority Phones
INSERT INTO "Authority_Phone" ("Authority_ID", "Phone_No") VALUES
(1, '02226471255'),
(1, '02226470916'),
(2, '02532512876'),
(2, '02532512867'),
(3, '02222620601'),
(3, '02222644832')
ON CONFLICT DO NOTHING;

-- 6. Students
INSERT INTO "Student" ("Student_ID", "First_Name", "Last_Name", "Email", "Enrollment_No", "Date_of_Birth", "Batch_Year", "House_no", "Street", "City", "State", "Pincode", "Department_ID", "Course_ID") VALUES
(1, 'Aditi', 'Shinde', 'aditi.shinde@kkwagh.edu.in', '2200490001', '2004-05-14', 2025, 'Flat 302', 'Gangapur Road', 'Nashik', 'Maharashtra', '422005', 1, 1),
(2, 'Rohan', 'Patil', 'rohan.patil@kkwagh.edu.in', '2200490002', '2003-11-20', 2025, 'B-12', 'College Road', 'Nashik', 'Maharashtra', '422005', 1, 1),
(3, 'Snehal', 'Deshmukh', 'snehal.deshmukh@kkwagh.edu.in', '2200490003', '2004-02-18', 2025, 'Plot 45', 'Indira Nagar', 'Nashik', 'Maharashtra', '422009', 2, 3),
(4, 'Pranav', 'Kulkarni', 'pranav.kulkarni@kkwagh.edu.in', '2200490004', '2003-08-09', 2025, 'Row House 3', 'Govind Nagar', 'Nashik', 'Maharashtra', '422009', 2, 4),
(5, 'Neha', 'Sharma', 'neha.sharma@kkwagh.edu.in', '2200490005', '2004-09-25', 2025, 'A-401', 'Panchavati', 'Nashik', 'Maharashtra', '422003', 3, 5),
(6, 'Aditya', 'Joshi', 'aditya.joshi@kkwagh.edu.in', '2200490006', '2003-04-12', 2025, '15/C', 'Ashok Nagar', 'Nashik', 'Maharashtra', '422012', 1, 2),
(7, 'Pooja', 'Gaikwad', 'pooja.gaikwad@kkwagh.edu.in', '2200490007', '2004-12-03', 2025, 'Shree Niwas', 'Ambad Link Road', 'Nashik', 'Maharashtra', '422010', 1, 1),
(8, 'Sanket', 'Wagh', 'sanket.wagh@kkwagh.edu.in', '2200490008', '2003-06-30', 2025, 'C-204', 'Amrutdham', 'Nashik', 'Maharashtra', '422003', 2, 3),
(9, 'Tanvi', 'More', 'tanvi.more@kkwagh.edu.in', '2200490009', '2004-07-22', 2025, 'Sneh Residency', 'Upnagar', 'Nashik', 'Maharashtra', '422006', 3, 5),
(10, 'Yash', 'Bhamare', 'yash.bhamare@kkwagh.edu.in', '2200490010', '2003-01-15', 2025, '7/Om Apt', 'Satpur Colony', 'Nashik', 'Maharashtra', '422007', 1, 2),
(11, 'Sakshi', 'Kale', 'sakshi.kale@kkwagh.edu.in', '2200490011', '2004-03-10', 2025, 'Bunglow 9', 'Mahatmanagar', 'Nashik', 'Maharashtra', '422007', 4, 7),
(12, 'Omkar', 'Shinde', 'omkar.shinde@kkwagh.edu.in', '2200490012', '2003-10-05', 2025, 'Flat 101', 'Anandwalli', 'Nashik', 'Maharashtra', '422013', 4, 7),
(13, 'Shruti', 'Jagtap', 'shruti.jagtap@kkwagh.edu.in', '2200490013', '2004-08-19', 2025, 'Plot 14', 'Rane Nagar', 'Nashik', 'Maharashtra', '422009', 5, 9),
(14, 'Tejas', 'Bagul', 'tejas.bagul@kkwagh.edu.in', '2200490014', '2003-05-27', 2025, '22/D', 'Cidco New Nashik', 'Nashik', 'Maharashtra', '422009', 5, 9),
(15, 'Rutuja', 'Nikam', 'rutuja.nikam@kkwagh.edu.in', '2200490015', '2004-11-11', 2025, 'Shanti Park', 'Jail Road', 'Nashik', 'Maharashtra', '422101', 6, 10),
(16, 'Sahil', 'Sonawane', 'sahil.sonawane@kkwagh.edu.in', '2200490016', '2003-09-02', 2025, '5/Prabhat', 'Mhasrul', 'Nashik', 'Maharashtra', '422004', 6, 10),
(17, 'Mansi', 'Wagh', 'mansi.wagh@kkwagh.edu.in', '2200490017', '2004-04-16', 2025, 'Sai Krupa', 'Adgaon Naka', 'Nashik', 'Maharashtra', '422003', 3, 6),
(18, 'Kunal', 'Khairnar', 'kunal.khairnar@kkwagh.edu.in', '2200490018', '2003-12-08', 2025, 'B-5', 'Trimurti Chowk', 'Nashik', 'Maharashtra', '422008', 4, 8),
(19, 'Neha', 'Gangurde', 'neha.gangurde@kkwagh.edu.in', '2200490019', '2004-06-21', 2025, '18/Krishna', 'Pathardi Phata', 'Nashik', 'Maharashtra', '422010', 2, 4),
(20, 'Parth', 'Salunke', 'parth.salunke@kkwagh.edu.in', '2200490020', '2003-02-14', 2025, '402/Silver', 'Dwarka Circle', 'Nashik', 'Maharashtra', '422011', 1, 1)
ON CONFLICT ("Student_ID") DO NOTHING;

SELECT setval(pg_get_serial_sequence('"Student"', 'Student_ID'), COALESCE(MAX("Student_ID"), 1)) FROM "Student";

-- 7. Student Phones
INSERT INTO "Student_Phone" ("Student_ID", "Phone_No") VALUES
(1, '9823012345'), (1, '9823012346'),
(2, '9823023456'), (3, '9823034567'),
(4, '9823045678'), (5, '9823056789'),
(6, '9823067890'), (7, '9823078901'),
(8, '9823089012'), (9, '9823090123'),
(10, '9823001234'), (11, '9823011223'),
(12, '9823022334'), (13, '9823033445'),
(14, '9823044556'), (15, '9823055667'),
(16, '9823066778'), (17, '9823077889'),
(18, '9823088990'), (19, '9823099001'),
(20, '9823000112')
ON CONFLICT DO NOTHING;

-- 8. Users
-- Passwords: admin/admin123, staff/staff123, examcell/exam123, student/student123
INSERT INTO "Users" ("User_ID", "Username", "Password_Hash", "Role", "Email", "Last_Login", "Student_ID") VALUES
(1, 'admin', 'scrypt:32768:8:1$7t8m7sB0U4Q3w8y9$8db8cf7a2a07cba57e93f350c3bc63554162ea330541d402919d7d49e6f3b06385cfd4eb95cb2e3e56b85e054ba9f4931a3ebfa98cb57ff5c9ba691515ef3c42', 'Admin', 'admin@kkwagh.edu.in', NOW(), NULL),
(2, 'staff', 'scrypt:32768:8:1$1u5n9sB0U4Q3w8y9$7ab8cf7a2a07cba57e93f350c3bc63554162ea330541d402919d7d49e6f3b06385cfd4eb95cb2e3e56b85e054ba9f4931a3ebfa98cb57ff5c9ba691515ef3c42', 'Staff', 'staff@kkwagh.edu.in', NOW(), NULL),
(3, 'examcell', 'scrypt:32768:8:1$9u2m9sB0U4Q3w8y9$6ab8cf7a2a07cba57e93f350c3bc63554162ea330541d402919d7d49e6f3b06385cfd4eb95cb2e3e56b85e054ba9f4931a3ebfa98cb57ff5c9ba691515ef3c42', 'Staff', 'exam_officer@kkwagh.edu.in', NOW(), NULL),
(4, 'student', 'scrypt:32768:8:1$2u5n9sB0U4Q3w8y9$5ab8cf7a2a07cba57e93f350c3bc63554162ea330541d402919d7d49e6f3b06385cfd4eb95cb2e3e56b85e054ba9f4931a3ebfa98cb57ff5c9ba691515ef3c42', 'Student', 'aditi.shinde@kkwagh.edu.in', NOW(), 1),
(5, 'rohan', 'scrypt:32768:8:1$3u5n9sB0U4Q3w8y9$4ab8cf7a2a07cba57e93f350c3bc63554162ea330541d402919d7d49e6f3b06385cfd4eb95cb2e3e56b85e054ba9f4931a3ebfa98cb57ff5c9ba691515ef3c42', 'Student', 'rohan.patil@kkwagh.edu.in', NOW(), 2),
(6, 'snehal', 'scrypt:32768:8:1$4u5n9sB0U4Q3w8y9$3ab8cf7a2a07cba57e93f350c3bc63554162ea330541d402919d7d49e6f3b06385cfd4eb95cb2e3e56b85e054ba9f4931a3ebfa98cb57ff5c9ba691515ef3c42', 'Student', 'snehal.deshmukh@kkwagh.edu.in', NOW(), 3)
ON CONFLICT ("User_ID") DO NOTHING;

SELECT setval(pg_get_serial_sequence('"Users"', 'User_ID'), COALESCE(MAX("User_ID"), 1)) FROM "Users";

-- 9. Certificates (Active, Expired, Revoked)
INSERT INTO "Certificate" ("Certificate_ID", "Certificate_Number", "Certificate_Name", "Student_ID", "Type_ID", "Authority_ID", "Issue_Date", "Expiry_Date", "Status", "Grade", "QR_Code", "Certificate_File") VALUES
(1, 'KKW-2024-00001', 'Diploma in Computer Technology', 1, 1, 1, '2024-06-15', NULL, 'Active', 'Dist.', 'uploads/qrcodes/qr_KKW-2024-00001.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(2, 'KKW-2024-00002', 'Annual Departmental Rank 1 Merit Certificate', 1, 2, 2, '2024-07-20', NULL, 'Active', 'A+', 'uploads/qrcodes/qr_KKW-2024-00002.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(3, 'KKW-2024-00003', 'Diploma in Computer Technology', 2, 1, 1, '2024-06-15', NULL, 'Active', 'First', 'uploads/qrcodes/qr_KKW-2024-00003.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(4, 'KKW-2024-00004', 'Diploma in Information Technology', 3, 1, 1, '2024-06-15', NULL, 'Active', 'Dist.', 'uploads/qrcodes/qr_KKW-2024-00004.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(5, 'KKW-2024-00005', 'Diploma in Cloud Computing & Cybersecurity', 4, 1, 2, '2024-06-20', NULL, 'Active', 'Dist.', 'uploads/qrcodes/qr_KKW-2024-00005.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(6, 'KKW-2024-00006', 'Diploma in Electronics & Telecommunication', 5, 1, 1, '2024-06-15', NULL, 'Active', 'First', 'uploads/qrcodes/qr_KKW-2024-00006.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(7, 'KKW-2024-00007', 'Advance Diploma in AI & Machine Learning', 6, 1, 2, '2024-07-01', NULL, 'Active', 'Dist.', 'uploads/qrcodes/qr_KKW-2024-00007.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(8, 'KKW-2024-00008', 'Diploma in Computer Technology', 7, 1, 1, '2024-06-15', NULL, 'Revoked', 'First', 'uploads/qrcodes/qr_KKW-2024-00008.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(9, 'KKW-2024-00009', 'Diploma in Information Technology', 8, 1, 1, '2024-06-15', NULL, 'Active', 'First', 'uploads/qrcodes/qr_KKW-2024-00009.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(10, 'KKW-2024-00010', 'Diploma in Electronics & Telecommunication', 9, 1, 1, '2024-06-15', NULL, 'Active', 'Dist.', 'uploads/qrcodes/qr_KKW-2024-00010.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(11, 'KKW-2024-00011', 'National Project Competition - First Place', 10, 4, 2, '2024-08-10', NULL, 'Active', 'Top Rank', 'uploads/qrcodes/qr_KKW-2024-00011.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(12, 'KKW-2023-00012', 'Industrial Python & IoT Workshop Certification', 1, 3, 2, '2023-01-15', '2024-01-15', 'Expired', 'A', 'uploads/qrcodes/qr_KKW-2023-00012.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(13, 'KKW-2023-00013', 'Certified Ethical Hacker Hands-on Training', 2, 3, 2, '2023-03-30', '2024-03-30', 'Expired', 'A+', 'uploads/qrcodes/qr_KKW-2023-00013.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(14, 'KKW-2024-00014', 'Certified Full-Stack Web Developer', 3, 3, 2, '2024-02-01', '2026-02-01', 'Revoked', 'B+', 'uploads/qrcodes/qr_KKW-2024-00014.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(15, 'KKW-2023-00015', 'Google Cloud Associate Engineering Workshop', 6, 3, 2, '2023-05-20', '2024-05-20', 'Expired', 'A', 'uploads/qrcodes/qr_KKW-2023-00015.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(16, 'KKW-2024-00016', 'Diploma in Mechanical Engineering', 11, 1, 1, '2024-06-15', NULL, 'Active', 'Dist.', 'uploads/qrcodes/qr_KKW-2024-00016.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(17, 'KKW-2024-00017', 'Diploma in Mechanical Engineering', 12, 1, 1, '2024-06-15', NULL, 'Active', 'First', 'uploads/qrcodes/qr_KKW-2024-00017.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(18, 'KKW-2024-00018', 'Diploma in Civil Engineering', 13, 1, 1, '2024-06-15', NULL, 'Active', 'Dist.', 'uploads/qrcodes/qr_KKW-2024-00018.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(19, 'KKW-2024-00019', 'Diploma in Civil Engineering', 14, 1, 1, '2024-06-15', NULL, 'Revoked', 'Pass', 'uploads/qrcodes/qr_KKW-2024-00019.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(20, 'KKW-2024-00020', 'Diploma in AI & Data Science', 15, 1, 1, '2024-06-15', NULL, 'Active', 'Dist.', 'uploads/qrcodes/qr_KKW-2024-00020.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(21, 'KKW-2024-00021', 'Diploma in AI & Data Science', 16, 1, 1, '2024-06-15', NULL, 'Active', 'First', 'uploads/qrcodes/qr_KKW-2024-00021.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(22, 'KKW-2024-00022', 'Diploma in VLSI & Embedded Systems', 17, 1, 2, '2024-07-05', NULL, 'Active', 'Dist.', 'uploads/qrcodes/qr_KKW-2024-00022.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(23, 'KKW-2024-00023', 'Diploma in Mechatronics & Automation', 18, 1, 1, '2024-06-15', NULL, 'Active', 'First', 'uploads/qrcodes/qr_KKW-2024-00023.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(24, 'KKW-2023-00024', 'In-Plant Industrial Training - Cloud Infrastructures', 19, 5, 3, '2023-07-01', '2024-07-01', 'Expired', 'A+', 'uploads/qrcodes/qr_KKW-2023-00024.png', 'uploads/certificates/sample_diploma_kkw.pdf'),
(25, 'KKW-2023-00025', 'Industrial Robotics & Computer Vision Certification', 20, 3, 2, '2023-08-15', '2024-08-15', 'Expired', 'Dist.', 'uploads/qrcodes/qr_KKW-2023-00025.png', 'uploads/certificates/sample_diploma_kkw.pdf')
ON CONFLICT ("Certificate_ID") DO NOTHING;

SELECT setval(pg_get_serial_sequence('"Certificate"', 'Certificate_ID'), COALESCE(MAX("Certificate_ID"), 1)) FROM "Certificate";

-- 10. Revocations (Weak Entity)
INSERT INTO "Revocation" ("Certificate_ID", "Revocation_No", "Reason", "Revoked_Date", "User_ID") VALUES
(8, 1, 'Falsified attendance and internal marks submission; disciplinary committee order #49/2025', '2025-01-10', 1),
(14, 1, 'Administrative recall due to syllabus non-compliance and revised examination criteria', '2025-02-15', 2),
(19, 1, 'Candidate failed prerequisite practical examination after scrutiny verification', '2025-03-02', 3)
ON CONFLICT DO NOTHING;

-- 11. Audit Logs
INSERT INTO "Audit_Log" ("Action", "Timestamp", "IP_Address", "User_ID") VALUES
('System Initialized with Master Schema and Seed Data', NOW() - INTERVAL '7 days', '127.0.0.1', 1),
('Created department ''Computer Technology''', NOW() - INTERVAL '6 days 5 hours', '127.0.0.1', 1),
('Created department ''Mechanical Engineering''', NOW() - INTERVAL '6 days 4 hours', '127.0.0.1', 1),
('Registered student ''Aditi Shinde'' (2200490001)', NOW() - INTERVAL '5 days 2 hours', '127.0.0.1', 2),
('Issued certificate KKW-2024-00001 to student 2200490001', NOW() - INTERVAL '4 days 8 hours', '127.0.0.1', 2),
('Revoked certificate KKW-2024-00008 (Reason: Disciplinary Committee Order)', NOW() - INTERVAL '3 days 2 hours', '127.0.0.1', 1),
('Revoked certificate KKW-2024-00019 (Reason: Prerequisite failed)', NOW() - INTERVAL '2 days 4 hours', '127.0.0.1', 3),
('Login successful for user ''admin''', NOW() - INTERVAL '2 hours', '127.0.0.1', 1),
('Public Verification Query: KKW-2024-00001 (Result: Found)', NOW() - INTERVAL '45 minutes', '192.168.1.15', 1);

-- 12. Notifications
INSERT INTO "Notification" ("Message", "Sent_Date", "Status", "User_ID") VALUES
('Welcome to EduDesk! Your administrator dashboard has been initialized.', NOW() - INTERVAL '5 days', 'Read', 1),
('Staff permissions configured. You can issue certificates and register student candidates.', NOW() - INTERVAL '4 days', 'Read', 2),
('Examination cell access authorized for summer 2025 diploma result certification.', NOW() - INTERVAL '3 days', 'Read', 3),
('Your certificate ''Diploma in Computer Technology'' (KKW-2024-00001) has been issued.', NOW() - INTERVAL '2 days', 'Unread', 4),
('Your certificate ''Annual Departmental Rank 1 Merit Certificate'' (KKW-2024-00002) has been issued.', NOW() - INTERVAL '12 hours', 'Unread', 4),
('Certificate ''Industrial Python & IoT Workshop'' (KKW-2023-00012) has expired.', NOW() - INTERVAL '4 hours', 'Unread', 4),
('Your certificate ''Diploma in Computer Technology'' (KKW-2024-00003) has been issued.', NOW() - INTERVAL '2 days', 'Unread', 5),
('Your certificate ''Diploma in Information Technology'' (KKW-2024-00004) has been issued.', NOW() - INTERVAL '2 days', 'Unread', 6);
