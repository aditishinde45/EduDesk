import os
import datetime
from app import create_app
from extensions import db
from models import (
    Department, Course, CertificateType, IssuingAuthority, AuthorityPhone,
    Student, StudentPhone, User, Certificate, Revocation, AuditLog, Notification
)
from utils.qr_generator import generate_certificate_qr

def seed_database():
    app = create_app()

    with app.app_context():
        print("🌱 Seeding EduDesk database...")

        # Clear existing data cleanly in reverse FK dependency order
        Revocation.query.delete()
        Notification.query.delete()
        AuditLog.query.delete()
        Certificate.query.delete()
        User.query.delete()
        StudentPhone.query.delete()
        Student.query.delete()
        AuthorityPhone.query.delete()
        IssuingAuthority.query.delete()
        CertificateType.query.delete()
        Course.query.delete()
        Department.query.delete()
        db.session.commit()

        # ---------------------------------------------------------------------
        # 1. Departments (3)
        # ---------------------------------------------------------------------
        dept_cm = Department(
            Department_Name="Computer Technology",
            HOD_Name="Prof. P. B. Patil",
            Email="hod_cm@kkwagh.edu.in"
        )
        dept_it = Department(
            Department_Name="Information Technology",
            HOD_Name="Prof. S. M. Deshmukh",
            Email="hod_it@kkwagh.edu.in"
        )
        dept_entc = Department(
            Department_Name="Electronics & Telecommunication",
            HOD_Name="Prof. V. K. Jadhav",
            Email="hod_entc@kkwagh.edu.in"
        )
        db.session.add_all([dept_cm, dept_it, dept_entc])
        db.session.flush()

        # ---------------------------------------------------------------------
        # 2. Courses (5)
        # ---------------------------------------------------------------------
        course_cm = Course(
            Course_Name="Diploma in Computer Technology",
            Duration="3 Years",
            Department_ID=dept_cm.Department_ID
        )
        course_aiml = Course(
            Course_Name="Advance Diploma in AI & Machine Learning",
            Duration="1 Year",
            Department_ID=dept_cm.Department_ID
        )
        course_it = Course(
            Course_Name="Diploma in Information Technology",
            Duration="3 Years",
            Department_ID=dept_it.Department_ID
        )
        course_cloud = Course(
            Course_Name="Diploma in Cloud Computing & Cybersecurity",
            Duration="2 Years",
            Department_ID=dept_it.Department_ID
        )
        course_entc = Course(
            Course_Name="Diploma in Electronics & Telecommunication",
            Duration="3 Years",
            Department_ID=dept_entc.Department_ID
        )
        db.session.add_all([course_cm, course_aiml, course_it, course_cloud, course_entc])
        db.session.flush()

        # ---------------------------------------------------------------------
        # 3. Certificate Types (4)
        # ---------------------------------------------------------------------
        type_diploma = CertificateType(
            Type_Name="Diploma Certificate",
            Description="Official MSBTE Diploma completion credential awarded upon completing the academic curriculum."
        )
        type_merit = CertificateType(
            Type_Name="Merit Certificate",
            Description="Awarded for academic excellence, departmental rank holders, and exceptional distinctions."
        )
        type_course = CertificateType(
            Type_Name="Course Completion",
            Description="Validating technical skill certifications and hands-on laboratory workshops."
        )
        type_project = CertificateType(
            Type_Name="Project Excellence",
            Description="Awarded for outstanding technical capstone projects, research, and engineering innovations."
        )
        db.session.add_all([type_diploma, type_merit, type_course, type_project])
        db.session.flush()

        # ---------------------------------------------------------------------
        # 4. Issuing Authorities (2) & Phones
        # ---------------------------------------------------------------------
        auth_msbte = IssuingAuthority(
            Authority_Name="Maharashtra State Board of Technical Education (MSBTE)",
            Registration_No="MSBTE-MUM-1963",
            Email="support@msbte.org.in",
            Website="https://msbte.org.in",
            House_no="49",
            Street="Kherwadi, Ali Yawar Jung Marg, Bandra (E)",
            City="Mumbai",
            State="Maharashtra",
            Pincode="400051"
        )
        auth_kkw = IssuingAuthority(
            Authority_Name="K. K. Wagh Polytechnic Examination Authority",
            Registration_No="KKW-POLY-EXAM-049",
            Email="exam_cell@kkwagh.edu.in",
            Website="https://poly.kkwagh.edu.in",
            House_no="Exam Cell Bldg",
            Street="Hirabai Haridas Vidyanagari, Amrutdham",
            City="Nashik",
            State="Maharashtra",
            Pincode="422003"
        )
        db.session.add_all([auth_msbte, auth_kkw])
        db.session.flush()

        # Authority Phones
        auth_phones = [
            AuthorityPhone(Authority_ID=auth_msbte.Authority_ID, Phone_No="02226471255"),
            AuthorityPhone(Authority_ID=auth_msbte.Authority_ID, Phone_No="02226470916"),
            AuthorityPhone(Authority_ID=auth_kkw.Authority_ID, Phone_No="02532512876"),
            AuthorityPhone(Authority_ID=auth_kkw.Authority_ID, Phone_No="02532512867")
        ]
        db.session.add_all(auth_phones)

        # ---------------------------------------------------------------------
        # 5. Students (10) & Student Phones
        # ---------------------------------------------------------------------
        students_data = [
            ("Aditi", "Shinde", "aditi.shinde@kkwagh.edu.in", "2200490001", datetime.date(2004, 5, 14), 2025, "Flat 302", "Gangapur Road", "Nashik", "Maharashtra", "422005", dept_cm.Department_ID, course_cm.Course_ID, ["9823012345", "9823012346"]),
            ("Rohan", "Patil", "rohan.patil@kkwagh.edu.in", "2200490002", datetime.date(2003, 11, 20), 2025, "B-12", "College Road", "Nashik", "Maharashtra", "422005", dept_cm.Department_ID, course_cm.Course_ID, ["9823023456"]),
            ("Snehal", "Deshmukh", "snehal.deshmukh@kkwagh.edu.in", "2200490003", datetime.date(2004, 2, 18), 2025, "Plot 45", "Indira Nagar", "Nashik", "Maharashtra", "422009", dept_it.Department_ID, course_it.Course_ID, ["9823034567"]),
            ("Pranav", "Kulkarni", "pranav.kulkarni@kkwagh.edu.in", "2200490004", datetime.date(2003, 8, 9), 2025, "Row House 3", "Govind Nagar", "Nashik", "Maharashtra", "422009", dept_it.Department_ID, course_cloud.Course_ID, ["9823045678"]),
            ("Neha", "Sharma", "neha.sharma@kkwagh.edu.in", "2200490005", datetime.date(2004, 9, 25), 2025, "A-401", "Panchavati", "Nashik", "Maharashtra", "422003", dept_entc.Department_ID, course_entc.Course_ID, ["9823056789"]),
            ("Aditya", "Joshi", "aditya.joshi@kkwagh.edu.in", "2200490006", datetime.date(2003, 4, 12), 2025, "15/C", "Ashok Nagar", "Nashik", "Maharashtra", "422012", dept_cm.Department_ID, course_aiml.Course_ID, ["9823067890"]),
            ("Pooja", "Gaikwad", "pooja.gaikwad@kkwagh.edu.in", "2200490007", datetime.date(2004, 12, 3), 2025, "Shree Niwas", "Ambad Link Road", "Nashik", "Maharashtra", "422010", dept_cm.Department_ID, course_cm.Course_ID, ["9823078901"]),
            ("Sanket", "Wagh", "sanket.wagh@kkwagh.edu.in", "2200490008", datetime.date(2003, 6, 30), 2025, "C-204", "Amrutdham", "Nashik", "Maharashtra", "422003", dept_it.Department_ID, course_it.Course_ID, ["9823089012"]),
            ("Tanvi", "More", "tanvi.more@kkwagh.edu.in", "2200490009", datetime.date(2004, 7, 22), 2025, "Sneh Residency", "Upnagar", "Nashik", "Maharashtra", "422006", dept_entc.Department_ID, course_entc.Course_ID, ["9823090123"]),
            ("Yash", "Bhamare", "yash.bhamare@kkwagh.edu.in", "2200490010", datetime.date(2003, 1, 15), 2025, "7/Om Apt", "Satpur Colony", "Nashik", "Maharashtra", "422007", dept_cm.Department_ID, course_aiml.Course_ID, ["9823001234"])
        ]

        created_students = []
        for s_data in students_data:
            stud = Student(
                First_Name=s_data[0],
                Last_Name=s_data[1],
                Email=s_data[2],
                Enrollment_No=s_data[3],
                Date_of_Birth=s_data[4],
                Batch_Year=s_data[5],
                House_no=s_data[6],
                Street=s_data[7],
                City=s_data[8],
                State=s_data[9],
                Pincode=s_data[10],
                Department_ID=s_data[11],
                Course_ID=s_data[12]
            )
            db.session.add(stud)
            db.session.flush()
            created_students.append(stud)

            for phone_no in s_data[13]:
                db.session.add(StudentPhone(Student_ID=stud.Student_ID, Phone_No=phone_no))

        # ---------------------------------------------------------------------
        # 6. Users (Admin, Staff, Student)
        # ---------------------------------------------------------------------
        user_admin = User(
            Username="admin",
            Role="Admin",
            Email="admin@kkwagh.edu.in",
            Last_Login=datetime.datetime.utcnow()
        )
        user_admin.set_password("admin123")

        user_staff = User(
            Username="staff",
            Role="Staff",
            Email="staff@kkwagh.edu.in",
            Last_Login=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
        )
        user_staff.set_password("staff123")

        user_student = User(
            Username="student",
            Role="Student",
            Email="aditi.shinde@kkwagh.edu.in",
            Student_ID=created_students[0].Student_ID,  # Linked to Aditi Shinde
            Last_Login=datetime.datetime.utcnow() - datetime.timedelta(hours=5)
        )
        user_student.set_password("student123")

        db.session.add_all([user_admin, user_staff, user_student])
        db.session.flush()

        # ---------------------------------------------------------------------
        # 7. Certificates (15) - Mix of Active (10), Expired (3), Revoked (2)
        # ---------------------------------------------------------------------
        # Create a sample certificate file on disk for demo download
        sample_cert_dir = app.config['CERTIFICATES_FOLDER']
        os.makedirs(sample_cert_dir, exist_ok=True)
        sample_file_path = os.path.join(sample_cert_dir, "sample_diploma_kkw.pdf")
        if not os.path.exists(sample_file_path):
            with open(sample_file_path, "wb") as f:
                f.write(b"%PDF-1.4\n% EduDesk Mock Academic Certificate Document\n%%EOF")

        certs_specs = [
            # 1. Aditi Shinde - Active Diploma
            ("KKW-2024-00001", "Diploma in Computer Technology", created_students[0].Student_ID, type_diploma.Type_ID, auth_msbte.Authority_ID, datetime.date(2024, 6, 15), None, "Active", "Dist."),
            # 2. Aditi Shinde - Active Merit
            ("KKW-2024-00002", "Annual Departmental Rank 1 Merit Certificate", created_students[0].Student_ID, type_merit.Type_ID, auth_kkw.Authority_ID, datetime.date(2024, 7, 20), None, "Active", "A+"),
            # 3. Rohan Patil - Active Diploma
            ("KKW-2024-00003", "Diploma in Computer Technology", created_students[1].Student_ID, type_diploma.Type_ID, auth_msbte.Authority_ID, datetime.date(2024, 6, 15), None, "Active", "First"),
            # 4. Snehal Deshmukh - Active Diploma
            ("KKW-2024-00004", "Diploma in Information Technology", created_students[2].Student_ID, type_diploma.Type_ID, auth_msbte.Authority_ID, datetime.date(2024, 6, 15), None, "Active", "Dist."),
            # 5. Pranav Kulkarni - Active Cloud Computing
            ("KKW-2024-00005", "Diploma in Cloud Computing & Cybersecurity", created_students[3].Student_ID, type_diploma.Type_ID, auth_kkw.Authority_ID, datetime.date(2024, 6, 20), None, "Active", "Dist."),
            # 6. Neha Sharma - Active ENTC
            ("KKW-2024-00006", "Diploma in Electronics & Telecommunication", created_students[4].Student_ID, type_diploma.Type_ID, auth_msbte.Authority_ID, datetime.date(2024, 6, 15), None, "Active", "First"),
            # 7. Aditya Joshi - Active AI ML
            ("KKW-2024-00007", "Advance Diploma in AI & Machine Learning", created_students[5].Student_ID, type_diploma.Type_ID, auth_kkw.Authority_ID, datetime.date(2024, 7, 1), None, "Active", "Dist."),
            # 8. Pooja Gaikwad - REVOKED
            ("KKW-2024-00008", "Diploma in Computer Technology", created_students[6].Student_ID, type_diploma.Type_ID, auth_msbte.Authority_ID, datetime.date(2024, 6, 15), None, "Revoked", "First"),
            # 9. Sanket Wagh - Active IT
            ("KKW-2024-00009", "Diploma in Information Technology", created_students[7].Student_ID, type_diploma.Type_ID, auth_msbte.Authority_ID, datetime.date(2024, 6, 15), None, "Active", "First"),
            # 10. Tanvi More - Active ENTC
            ("KKW-2024-00010", "Diploma in Electronics & Telecommunication", created_students[8].Student_ID, type_diploma.Type_ID, auth_msbte.Authority_ID, datetime.date(2024, 6, 15), None, "Active", "Dist."),
            # 11. Yash Bhamare - Active Project Excellence
            ("KKW-2024-00011", "National Project Competition - First Place", created_students[9].Student_ID, type_project.Type_ID, auth_kkw.Authority_ID, datetime.date(2024, 8, 10), None, "Active", "Top Rank"),
            # 12. Aditi Shinde - EXPIRED course certificate (Expired on 2024-01-15)
            ("KKW-2023-00012", "Industrial Python & IoT Workshop Certification", created_students[0].Student_ID, type_course.Type_ID, auth_kkw.Authority_ID, datetime.date(2023, 1, 15), datetime.date(2024, 1, 15), "Expired", "A"),
            # 13. Rohan Patil - EXPIRED cybersecurity certificate (Expired on 2024-03-30)
            ("KKW-2023-00013", "Certified Ethical Hacker Hands-on Training", created_students[1].Student_ID, type_course.Type_ID, auth_kkw.Authority_ID, datetime.date(2023, 3, 30), datetime.date(2024, 3, 30), "Expired", "A+"),
            # 14. Snehal Deshmukh - REVOKED certificate
            ("KKW-2024-00014", "Certified Full-Stack Web Developer", created_students[2].Student_ID, type_course.Type_ID, auth_kkw.Authority_ID, datetime.date(2024, 2, 1), datetime.date(2026, 2, 1), "Revoked", "B+"),
            # 15. Aditya Joshi - EXPIRED Cloud certification (Expired on 2024-05-20)
            ("KKW-2023-00015", "Google Cloud Associate Engineering Workshop", created_students[5].Student_ID, type_course.Type_ID, auth_kkw.Authority_ID, datetime.date(2023, 5, 20), datetime.date(2024, 5, 20), "Expired", "A")
        ]

        created_certs = []
        for spec in certs_specs:
            cert_no = spec[0]
            # Generate actual QR code on disk
            qr_rel_path = generate_certificate_qr(cert_no, f"/verify/{cert_no}")

            cert = Certificate(
                Certificate_Number=cert_no,
                Certificate_Name=spec[1],
                Student_ID=spec[2],
                Type_ID=spec[3],
                Authority_ID=spec[4],
                Issue_Date=spec[5],
                Expiry_Date=spec[6],
                Status=spec[7],
                Grade=spec[8],
                QR_Code=qr_rel_path,
                Certificate_File="uploads/certificates/sample_diploma_kkw.pdf"
            )
            db.session.add(cert)
            db.session.flush()
            created_certs.append(cert)

        # ---------------------------------------------------------------------
        # 8. Revocations (WEAK Entity: Composite PK (Certificate_ID, Revocation_No))
        # ---------------------------------------------------------------------
        # Revoke cert 8 (Pooja Gaikwad)
        rev_1 = Revocation(
            Certificate_ID=created_certs[7].Certificate_ID,
            Revocation_No=1,
            Reason="Falsified attendance and internal marks submission; disciplinary committee order #49/2025",
            Revoked_Date=datetime.date(2025, 1, 10),
            User_ID=user_admin.User_ID
        )

        # Revoke cert 14 (Snehal Deshmukh)
        rev_2 = Revocation(
            Certificate_ID=created_certs[13].Certificate_ID,
            Revocation_No=1,
            Reason="Administrative recall due to syllabus non-compliance and revised examination criteria",
            Revoked_Date=datetime.date(2025, 2, 15),
            User_ID=user_staff.User_ID
        )
        db.session.add_all([rev_1, rev_2])

        # ---------------------------------------------------------------------
        # 9. Audit Logs
        # ---------------------------------------------------------------------
        sample_logs = [
            AuditLog(Action="System Initialized with Master Schema and Seed Data", Timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=3), IP_Address="127.0.0.1", User_ID=user_admin.User_ID),
            AuditLog(Action="Created department 'Computer Technology'", Timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=2, hours=5), IP_Address="127.0.0.1", User_ID=user_admin.User_ID),
            AuditLog(Action="Registered student 'Aditi Shinde' (2200490001)", Timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=2, hours=3), IP_Address="127.0.0.1", User_ID=user_staff.User_ID),
            AuditLog(Action="Issued certificate KKW-2024-00001 to student 2200490001", Timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=1, hours=8), IP_Address="127.0.0.1", User_ID=user_staff.User_ID),
            AuditLog(Action="Revoked certificate KKW-2024-00008 (Reason: Disciplinary Committee Order)", Timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=1, hours=2), IP_Address="127.0.0.1", User_ID=user_admin.User_ID),
            AuditLog(Action="Login successful for user 'admin'", Timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=1), IP_Address="127.0.0.1", User_ID=user_admin.User_ID),
            AuditLog(Action="Public Verification Query: KKW-2024-00001 (Result: Found)", Timestamp=datetime.datetime.utcnow() - datetime.timedelta(minutes=30), IP_Address="192.168.1.15", User_ID=user_admin.User_ID)
        ]
        db.session.add_all(sample_logs)

        # ---------------------------------------------------------------------
        # 10. Notifications
        # ---------------------------------------------------------------------
        sample_notifs = [
            Notification(Message="Welcome to EduDesk! Your administrator dashboard has been initialized.", Sent_Date=datetime.datetime.utcnow() - datetime.timedelta(days=3), Status="Read", User_ID=user_admin.User_ID),
            Notification(Message="Staff permissions configured. You can issue certificates and register student candidates.", Sent_Date=datetime.datetime.utcnow() - datetime.timedelta(days=2), Status="Read", User_ID=user_staff.User_ID),
            Notification(Message="Your certificate 'Diploma in Computer Technology' (KKW-2024-00001) has been issued.", Sent_Date=datetime.datetime.utcnow() - datetime.timedelta(days=1), Status="Unread", User_ID=user_student.User_ID),
            Notification(Message="Your certificate 'Annual Departmental Rank 1 Merit Certificate' (KKW-2024-00002) has been issued.", Sent_Date=datetime.datetime.utcnow() - datetime.timedelta(hours=6), Status="Unread", User_ID=user_student.User_ID),
            Notification(Message="Certificate 'Industrial Python & IoT Workshop' (KKW-2023-00012) has expired.", Sent_Date=datetime.datetime.utcnow() - datetime.timedelta(hours=1), Status="Unread", User_ID=user_student.User_ID)
        ]
        db.session.add_all(sample_notifs)

        db.session.commit()
        print("✅ Database successfully seeded with:")
        print(f"   - 3 Departments, 5 Courses")
        print(f"   - 4 Certificate Types, 2 Issuing Authorities (with phones)")
        print(f"   - 10 Students (with phones)")
        print(f"   - 3 Users: Admin (admin/admin123), Staff (staff/staff123), Student (student/student123)")
        print(f"   - 15 Certificates: 10 Active, 3 Expired, 2 Revoked (with QR codes and files)")
        print(f"   - 2 Revocation records (weak entity with composite PK)")
        print(f"   - Sample Audit Logs and Notifications")

if __name__ == '__main__':
    seed_database()
