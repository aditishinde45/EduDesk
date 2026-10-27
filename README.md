# EduDesk - Certificate Management System
### K. K. Wagh Institute of Engineering Education & Research (Polytechnic), Nashik

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1-black.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)

**EduDesk** is an enterprise-grade, secure, and clean Certificate Management and Public Verification System custom-built for **K. K. Wagh Polytechnic, Nashik**. It implements complete relational database principles (ER modeling, normalization, composite keys, weak entities, foreign key CASCADE/RESTRICT constraints, and derived attributes) paired with a responsive server-rendered web application.

---

## 🏛️ System Features

1. **Role-Based Access Control (RBAC)**:
   - Server-side enforced decorators (`@role_required`) protecting all endpoints.
   - Dynamic UI sidebar and action buttons adapting strictly to the user's role.
   - Friendly custom `403 Forbidden` error handling.
2. **Student Data Isolation**:
   - Students can only view their own personal profile, credentials, and notifications.
   - Strict server-side verification blocks students from accessing other candidates' records.
3. **Public Certificate Verification Portal (`/verify` & `/verify/<cert_no>`)**:
   - No login required.
   - Real-time validity checks returning **VALID / ACTIVE**, **EXPIRED**, or **REVOKED** statuses.
   - Displays student name, enrollment number, department, course, grade, and issuing authority.
   - Displays revocation reason and official audit date if revoked.
4. **QR Code Generation**:
   - Auto-generates scannable QR code PNGs via the `qrcode` library on certificate creation.
   - Encodes direct verification URL; displays on certificate cards and printable certificates.
5. **Printable Certificate Layout (`/certificates/<id>/print`)**:
   - High-resolution, printable certificate layout complete with institute seal, watermarks, signature blocks, and QR code verification stamp.
6. **Weak Entity Revocation System**:
   - `Revocation` entity with composite primary key `(Certificate_ID, Revocation_No)`.
   - Records revocation reason, date, and user ID; automatically sets certificate status to `Revoked`.
   - Dispatches automated notifications to students and administrative audit logs.
7. **Auto-Expiry Handling**:
   - Real-time check updating `Status = 'Expired'` whenever certificates pass their `Expiry_Date`.
   - Alerts students 30 days prior to certificate expiration.
8. **Relational Constraints & Integrity Protection**:
   - `ON DELETE RESTRICT` foreign keys prevent accidental deletion of parent records (Departments, Courses, Students, Authorities).
   - Catches `IntegrityError` and presents user-friendly alert messages instead of raw database crashes.
9. **Derived Attribute Calculation**:
   - `Age` is computed dynamically from `Date_of_Birth` both in SQL (`TIMESTAMPDIFF`) and in the application runtime. It is **never** stored in the database.
10. **Audit Trail & Notifications**:
    - Automatic immutable logging of user logins, logouts, record creation, updates, deletions, and revocations with client IP addresses.
    - Notification bell with unread badge counter in top navbar.
11. **Comprehensive Reports with CSV Export**:
    - Issued Certificates Report with date range and department filters.
    - Expired Certificates Report.
    - Certification Summary Report (counts grouped by category, department, and status).

---

## 🔐 Role Permission Matrix

| Module / Table | Admin | Staff | Student |
|---|---|---|---|
| **Users** (Create / Edit / Delete / Reset Password) | **Full CRUD** | No access | No access |
| **Audit_Log** | **Read only** | No access | No access |
| **Department**, **Course** | **Full CRUD** | **Read only** | No access |
| **Certificate_Type**, **Issuing_Authority**, **Authority_Phone** | **Full CRUD** | **Full CRUD** | No access |
| **Student**, **Student_Phone** | **Full CRUD** | **Create / Read / Update** (No delete) | **Read own profile only** |
| **Certificate** | **Full CRUD** | **Create / Read / Update** (No delete) | **Read + download own only** |
| **Revocation** | **Full CRUD** | **Create (revoke) + Read** | **Read own revoked only** |
| **Notification** | **Read all** | **Read own** | **Read own, mark as read** |
| **Reports** (Issued, Expired, Summary + CSV Export) | **Full access** | **Full access** | No access |

---

## 🗄️ Relational Database Schema (Tables 5.1 to 5.12)

The MySQL database schema follows the table specifications exactly:

1. **`Department`**: `Department_ID` (PK AI), `Department_Name` (UQ), `HOD_Name`, `Email` (UQ)
2. **`Course`**: `Course_ID` (PK AI), `Course_Name`, `Duration`, `Department_ID` (FK -> `Department` ON DELETE RESTRICT ON UPDATE CASCADE)
3. **`Certificate_Type`**: `Type_ID` (PK AI), `Type_Name` (UQ), `Description`
4. **`Issuing_Authority`**: `Authority_ID` (PK AI), `Authority_Name`, `Registration_No` (UQ), `Email`, `Website`, `House_no`, `Street`, `City`, `State`, `Pincode`
5. **`Authority_Phone`**: `Authority_ID` (PK, FK -> `Issuing_Authority` ON DELETE CASCADE ON UPDATE CASCADE), `Phone_No` (PK)
6. **`Student`**: `Student_ID` (PK AI), `First_Name`, `Last_Name`, `Email` (UQ), `Enrollment_No` (UQ), `Date_of_Birth`, `Batch_Year`, `House_no`, `Street`, `City`, `State`, `Pincode`, `Department_ID` (FK -> `Department` RESTRICT/CASCADE), `Course_ID` (FK -> `Course` RESTRICT/CASCADE). *`Age` is derived from `Date_of_Birth`.*
7. **`Student_Phone`**: `Student_ID` (PK, FK -> `Student` ON DELETE CASCADE ON UPDATE CASCADE), `Phone_No` (PK)
8. **`Users`**: `User_ID` (PK AI), `Username` (UQ), `Password_Hash`, `Role` (`Admin`, `Staff`, `Student`), `Email` (UQ), `Last_Login`, `Student_ID` (FK -> `Student` ON DELETE SET NULL ON UPDATE CASCADE)
9. **`Certificate`**: `Certificate_ID` (PK AI), `Certificate_Number` (UQ), `Certificate_Name`, `Issue_Date`, `Expiry_Date`, `Status` (`Active`, `Expired`, `Revoked`), `Grade`, `QR_Code`, `Certificate_File`, `Student_ID` (FK -> `Student`), `Type_ID` (FK -> `Certificate_Type`), `Authority_ID` (FK -> `Issuing_Authority`) — all three RESTRICT/CASCADE.
10. **`Revocation`** *(Weak Entity)*: `Certificate_ID` (PK, FK -> `Certificate` ON DELETE CASCADE ON UPDATE CASCADE), `Revocation_No` (PK partial key), `Reason`, `Revoked_Date`, `User_ID` (FK -> `Users` ON DELETE RESTRICT ON UPDATE CASCADE). Primary Key: `(Certificate_ID, Revocation_No)`
11. **`Audit_Log`**: `Log_ID` (PK AI), `Action`, `Timestamp`, `IP_Address`, `User_ID` (FK -> `Users` RESTRICT/CASCADE)
12. **`Notification`**: `Notification_ID` (PK AI), `Message`, `Sent_Date`, `Status`, `User_ID` (FK -> `Users` CASCADE/CASCADE)

---

## 🚀 Setup & Execution Instructions

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- MySQL Server 8.0+

### 2. Clone and Navigate to Directory
```bash
cd /Users/aditibhaskarshinde/DBMS_MICRO_project/EduDesk
```

### 3. Create & Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables (`.env`)
Copy `.env.example` to `.env` or edit `.env`:
```ini
SECRET_KEY=kkw-polytechnic-secret-key-2026-very-secure
DEBUG=True

# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=edudesk_db
DB_USER=root
DB_PASSWORD=your_mysql_password

# Direct SQLAlchemy URL
DATABASE_URL=mysql+pymysql://root:your_mysql_password@localhost:3306/edudesk_db
```

### 6. Create Database and Run Schema
Using MySQL CLI:
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS edudesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p edudesk_db < schema.sql
```

### 7. Seed Sample Data
Execute the seed script to create test accounts, academic structures, students, certificates, QR codes, and revocations:
```bash
python seed.py
```

### 8. Run the Application
```bash
python app.py
# or
python run.py
```
Open your browser at: **`http://127.0.0.1:5000`**

### 9. Run the Automated Test Suite
To verify all 10 role permissions, data isolation, and verification test cases:
```bash
python -W ignore -m unittest -v test_app.py
```

---

## 🔑 Default Test Credentials

| Role | Username | Password | Access Capabilities |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | Full CRUD on all modules, User management, Password resets, System Audit Logs |
| **Staff** | `staff` | `staff123` | Read Academics, Full CRUD on Authorities & Cert Types, Issue & Revoke Certs, Reports |
| **Student** | `student` | `student123` | Dedicated Student Portal, View & Download own certificates only, Profile view |

---

## 🌐 Key Pages & Endpoints

- **`/` or `/dashboard`**: Role-adaptive Dashboard
- **`/verify`**: Public Certificate Verification Portal (No login required)
- **`/verify/<certificate_number>`**: Public certificate verification result with QR code validation
- **`/certificates`**: Certificate directory (Auto-filtered for students)
- **`/certificates/<id>`**: Certificate detail page with QR code and revocation controls
- **`/certificates/<id>/print`**: High-resolution printable certificate layout
- **`/certificates/<id>/download`**: Download uploaded certificate PDF/Image
- **`/students`**: Student directory with computed derived Age badges
- **`/students/profile`**: Personal student profile
- **`/revocations`**: Register of revoked credentials
- **`/users`**: User account management and password resets (Admin only)
- **`/audit-logs`**: Immutable security audit trail with user and date filters (Admin only)
- **`/notifications`**: System notification center with unread bell counter
- **`/reports/issued`**: Issued certificates report with date range filter + CSV export
- **`/reports/expired`**: Expired certificates list + CSV export
- **`/reports/summary`**: Status breakdowns by category and department + CSV export

---

## 👨‍💻 Project Information
- **Institution**: K. K. Wagh Institute of Engineering Education & Research (Polytechnic), Nashik
- **Subject**: Database Management Systems (DBMS) Micro Project
- **Project Name**: EduDesk - College Certificate Management and Verification System
