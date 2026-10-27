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
        print("🌱 Seeding EduDesk database for K. K. Wagh Institute of Engineering Education & Research (KKWIEER), Nashik...")

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
        # 1. Engineering Departments (6)
        # ---------------------------------------------------------------------
        dept_comp = Department(
            Department_Name="Computer Engineering",
            HOD_Name="Prof. Dr. S. S. Sane",
            Email="hod_comp@kkwagh.edu.in"
        )
        dept_it = Department(
            Department_Name="Information Technology",
            HOD_Name="Dr. V. C. Bagal",
            Email="hod_it@kkwagh.edu.in"
        )
        dept_entc = Department(
            Department_Name="Electronics & Telecommunication",
            HOD_Name="Dr. D. M. Chandwadkar",
            Email="hod_entc@kkwagh.edu.in"
        )
        dept_mech = Department(
            Department_Name="Mechanical Engineering",
            HOD_Name="Dr. P. B. Kushare",
            Email="hod_mech@kkwagh.edu.in"
        )
        dept_civil = Department(
            Department_Name="Civil Engineering",
            HOD_Name="Dr. P. D. Jadhao",
            Email="hod_civil@kkwagh.edu.in"
        )
        dept_aids = Department(
            Department_Name="Artificial Intelligence & Data Science",
            HOD_Name="Dr. P. D. Bhamre",
            Email="hod_aids@kkwagh.edu.in"
        )
        db.session.add_all([dept_comp, dept_it, dept_entc, dept_mech, dept_civil, dept_aids])
        db.session.flush()

        # ---------------------------------------------------------------------
        # 2. Engineering Degree Courses (10)
        # ---------------------------------------------------------------------
        course_comp = Course(
            Course_Name="B.Tech in Computer Engineering",
            Duration="4 Years (8 Semesters)",
            Department_ID=dept_comp.Department_ID
        )
        course_aiml = Course(
            Course_Name="B.Tech in AI & Machine Learning (Honors)",
            Duration="4 Years (8 Semesters)",
            Department_ID=dept_comp.Department_ID
        )
        course_it = Course(
            Course_Name="B.Tech in Information Technology",
            Duration="4 Years (8 Semesters)",
            Department_ID=dept_it.Department_ID
        )
        course_cloud = Course(
            Course_Name="B.Tech in Cloud Computing & Cybersecurity",
            Duration="4 Years (8 Semesters)",
            Department_ID=dept_it.Department_ID
        )
        course_entc = Course(
            Course_Name="B.Tech in Electronics & Telecommunication",
            Duration="4 Years (8 Semesters)",
            Department_ID=dept_entc.Department_ID
        )
        course_vlsi = Course(
            Course_Name="B.Tech in VLSI & Embedded Systems (Honors)",
            Duration="4 Years (8 Semesters)",
            Department_ID=dept_entc.Department_ID
        )
        course_mech = Course(
            Course_Name="B.Tech in Mechanical Engineering",
            Duration="4 Years (8 Semesters)",
            Department_ID=dept_mech.Department_ID
        )
        course_mecha = Course(
            Course_Name="B.Tech in Robotics & Industrial Automation",
            Duration="4 Years (8 Semesters)",
            Department_ID=dept_mech.Department_ID
        )
        course_civil = Course(
            Course_Name="B.Tech in Civil Engineering",
            Duration="4 Years (8 Semesters)",
            Department_ID=dept_civil.Department_ID
        )
        course_aids = Course(
            Course_Name="B.Tech in AI & Data Science",
            Duration="4 Years (8 Semesters)",
            Department_ID=dept_aids.Department_ID
        )
        db.session.add_all([
            course_comp, course_aiml, course_it, course_cloud,
            course_entc, course_vlsi, course_mech, course_mecha,
            course_civil, course_aids
        ])
        db.session.flush()

        # ---------------------------------------------------------------------
        # 3. Engineering Certificate Types (6)
        # ---------------------------------------------------------------------
        type_degree = CertificateType(
            Type_Name="Degree Certificate (B.Tech)",
            Description="Official Bachelor of Technology degree credential conferred under autonomous university statutes."
        )
        type_transcript = CertificateType(
            Type_Name="Semester Grade Card / Transcript",
            Description="Official Autonomous Engineering Grade Report verifying SGPA, CGPA, and earned semester credits."
        )
        type_project = CertificateType(
            Type_Name="Capstone Engineering Project",
            Description="Validating completion, system design, and defense of senior undergraduate capstone project."
        )
        type_internship = CertificateType(
            Type_Name="Industrial Internship Credential",
            Description="Official accreditation of mandatory 6-month industrial internship with corporate technology partners."
        )
        type_symposium = CertificateType(
            Type_Name="Technical Symposium Award",
            Description="Recognizing excellence in national technical paper presentations, hackathons, and innovation contests."
        )
        type_honors = CertificateType(
            Type_Name="Honors & Minors Specialization",
            Description="Endorsement for completing advanced interdisciplinary specialized credit pathways (e.g. AI/ML, Cloud)."
        )
        db.session.add_all([type_degree, type_transcript, type_project, type_internship, type_symposium, type_honors])
        db.session.flush()

        # ---------------------------------------------------------------------
        # 4. Engineering Issuing Authorities (3) & Phone Numbers
        # ---------------------------------------------------------------------
        auth_coe = IssuingAuthority(
            Authority_Name="Office of Controller of Examinations (CoE), KKWIEER",
            Registration_No="KKWIEER-AUT-COE-01",
            Email="coe@kkwagh.edu.in",
            Website="https://engg.kkwagh.edu.in",
            House_no="Exam Cell Bldg",
            Street="Hirabai Haridas Vidyanagari, Amrutdham",
            City="Nashik",
            State="Maharashtra",
            Pincode="422003"
        )
        auth_dir = IssuingAuthority(
            Authority_Name="Office of the Principal & Director, KKWIEER",
            Registration_No="KKWIEER-DIR-001",
            Email="principal@kkwagh.edu.in",
            Website="https://engg.kkwagh.edu.in",
            House_no="Administrative Wing",
            Street="Hirabai Haridas Vidyanagari, Amrutdham",
            City="Nashik",
            State="Maharashtra",
            Pincode="422003"
        )
        auth_tnp = IssuingAuthority(
            Authority_Name="Training & Placement Cell (T&P), KKWIEER",
            Registration_No="KKWIEER-TNP-004",
            Email="placements@kkwagh.edu.in",
            Website="https://engg.kkwagh.edu.in/placements",
            House_no="Corporate Relations Center",
            Street="Hirabai Haridas Vidyanagari, Amrutdham",
            City="Nashik",
            State="Maharashtra",
            Pincode="422003"
        )
        db.session.add_all([auth_coe, auth_dir, auth_tnp])
        db.session.flush()

        # Authority Phones
        auth_phones = [
            AuthorityPhone(Authority_ID=auth_coe.Authority_ID, Phone_No="02532512876"),
            AuthorityPhone(Authority_ID=auth_coe.Authority_ID, Phone_No="02532512867"),
            AuthorityPhone(Authority_ID=auth_dir.Authority_ID, Phone_No="02532512877"),
            AuthorityPhone(Authority_ID=auth_dir.Authority_ID, Phone_No="02532512878"),
            AuthorityPhone(Authority_ID=auth_tnp.Authority_ID, Phone_No="02532512890"),
            AuthorityPhone(Authority_ID=auth_tnp.Authority_ID, Phone_No="02532512891")
        ]
        db.session.add_all(auth_phones)

        # ---------------------------------------------------------------------
        # 5. Engineering Undergrad Students (20) & Phones
        # ---------------------------------------------------------------------
        students_data = [
            ("Aditi", "Shinde", "aditi.shinde@kkwagh.edu.in", "2021BTECS001", datetime.date(2003, 5, 14), 2025, "Flat 302", "Gangapur Road", "Nashik", "Maharashtra", "422005", dept_comp.Department_ID, course_comp.Course_ID, ["9823012345", "9823012346"]),
            ("Rohan", "Patil", "rohan.patil@kkwagh.edu.in", "2021BTECS002", datetime.date(2003, 11, 20), 2025, "B-12", "College Road", "Nashik", "Maharashtra", "422005", dept_comp.Department_ID, course_comp.Course_ID, ["9823023456"]),
            ("Snehal", "Deshmukh", "snehal.deshmukh@kkwagh.edu.in", "2021BTIT003", datetime.date(2003, 2, 18), 2025, "Plot 45", "Indira Nagar", "Nashik", "Maharashtra", "422009", dept_it.Department_ID, course_it.Course_ID, ["9823034567"]),
            ("Pranav", "Kulkarni", "pranav.kulkarni@kkwagh.edu.in", "2021BTIT004", datetime.date(2002, 8, 9), 2025, "Row House 3", "Govind Nagar", "Nashik", "Maharashtra", "422009", dept_it.Department_ID, course_cloud.Course_ID, ["9823045678"]),
            ("Neha", "Sharma", "neha.sharma@kkwagh.edu.in", "2021BTENTC005", datetime.date(2003, 9, 25), 2025, "A-401", "Panchavati", "Nashik", "Maharashtra", "422003", dept_entc.Department_ID, course_entc.Course_ID, ["9823056789"]),
            ("Aditya", "Joshi", "aditya.joshi@kkwagh.edu.in", "2021BTECS006", datetime.date(2002, 4, 12), 2025, "15/C", "Ashok Nagar", "Nashik", "Maharashtra", "422012", dept_comp.Department_ID, course_aiml.Course_ID, ["9823067890"]),
            ("Pooja", "Gaikwad", "pooja.gaikwad@kkwagh.edu.in", "2021BTECS007", datetime.date(2003, 12, 3), 2025, "Shree Niwas", "Ambad Link Road", "Nashik", "Maharashtra", "422010", dept_comp.Department_ID, course_comp.Course_ID, ["9823078901"]),
            ("Sanket", "Wagh", "sanket.wagh@kkwagh.edu.in", "2021BTIT008", datetime.date(2002, 6, 30), 2025, "C-204", "Amrutdham", "Nashik", "Maharashtra", "422003", dept_it.Department_ID, course_it.Course_ID, ["9823089012"]),
            ("Tanvi", "More", "tanvi.more@kkwagh.edu.in", "2021BTENTC009", datetime.date(2003, 7, 22), 2025, "Sneh Residency", "Upnagar", "Nashik", "Maharashtra", "422006", dept_entc.Department_ID, course_entc.Course_ID, ["9823090123"]),
            ("Yash", "Bhamare", "yash.bhamare@kkwagh.edu.in", "2021BTECS010", datetime.date(2002, 1, 15), 2025, "7/Om Apt", "Satpur Colony", "Nashik", "Maharashtra", "422007", dept_comp.Department_ID, course_aiml.Course_ID, ["9823001234"]),
            ("Sakshi", "Kale", "sakshi.kale@kkwagh.edu.in", "2021BTME011", datetime.date(2003, 3, 10), 2025, "Bunglow 9", "Mahatmanagar", "Nashik", "Maharashtra", "422007", dept_mech.Department_ID, course_mech.Course_ID, ["9823011223"]),
            ("Omkar", "Shinde", "omkar.shinde@kkwagh.edu.in", "2021BTME012", datetime.date(2002, 10, 5), 2025, "Flat 101", "Anandwalli", "Nashik", "Maharashtra", "422013", dept_mech.Department_ID, course_mech.Course_ID, ["9823022334"]),
            ("Shruti", "Jagtap", "shruti.jagtap@kkwagh.edu.in", "2021BTCE013", datetime.date(2003, 8, 19), 2025, "Plot 14", "Rane Nagar", "Nashik", "Maharashtra", "422009", dept_civil.Department_ID, course_civil.Course_ID, ["9823033445"]),
            ("Tejas", "Bagul", "tejas.bagul@kkwagh.edu.in", "2021BTCE014", datetime.date(2002, 5, 27), 2025, "22/D", "Cidco New Nashik", "Nashik", "Maharashtra", "422009", dept_civil.Department_ID, course_civil.Course_ID, ["9823044556"]),
            ("Rutuja", "Nikam", "rutuja.nikam@kkwagh.edu.in", "2021BTAIDS015", datetime.date(2003, 11, 11), 2025, "Shanti Park", "Jail Road", "Nashik", "Maharashtra", "422101", dept_aids.Department_ID, course_aids.Course_ID, ["9823055667"]),
            ("Sahil", "Sonawane", "sahil.sonawane@kkwagh.edu.in", "2021BTAIDS016", datetime.date(2002, 9, 2), 2025, "5/Prabhat", "Mhasrul", "Nashik", "Maharashtra", "422004", dept_aids.Department_ID, course_aids.Course_ID, ["9823066778"]),
            ("Mansi", "Wagh", "mansi.wagh@kkwagh.edu.in", "2021BTENTC017", datetime.date(2003, 4, 16), 2025, "Sai Krupa", "Adgaon Naka", "Nashik", "Maharashtra", "422003", dept_entc.Department_ID, course_vlsi.Course_ID, ["9823077889"]),
            ("Kunal", "Khairnar", "kunal.khairnar@kkwagh.edu.in", "2021BTME018", datetime.date(2002, 12, 8), 2025, "B-5", "Trimurti Chowk", "Nashik", "Maharashtra", "422008", dept_mech.Department_ID, course_mecha.Course_ID, ["9823088990"]),
            ("Neha", "Gangurde", "neha.gangurde@kkwagh.edu.in", "2021BTIT019", datetime.date(2003, 6, 21), 2025, "18/Krishna", "Pathardi Phata", "Nashik", "Maharashtra", "422010", dept_it.Department_ID, course_cloud.Course_ID, ["9823099001"]),
            ("Parth", "Salunke", "parth.salunke@kkwagh.edu.in", "2021BTECS020", datetime.date(2002, 2, 14), 2025, "402/Silver", "Dwarka Circle", "Nashik", "Maharashtra", "422011", dept_comp.Department_ID, course_comp.Course_ID, ["9823000112"])
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
        # 6. Users (Admin, Staff, Controller of Exams, Students)
        # ---------------------------------------------------------------------
        user_admin = User(
            Username="admin",
            Role="Admin",
            Email="admin@kkwagh.edu.in",
            Last_Login=datetime.datetime.now(datetime.timezone.utc)
        )
        user_admin.set_password("admin123")

        user_staff = User(
            Username="staff",
            Role="Staff",
            Email="staff@kkwagh.edu.in",
            Last_Login=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2)
        )
        user_staff.set_password("staff123")

        user_exam = User(
            Username="examcell",
            Role="Staff",
            Email="coe_office@kkwagh.edu.in",
            Last_Login=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3)
        )
        user_exam.set_password("exam123")

        # Student users with linked Student_ID accounts
        user_student1 = User(
            Username="student",
            Role="Student",
            Email="aditi.shinde@kkwagh.edu.in",
            Student_ID=created_students[0].Student_ID,  # Aditi Shinde (Computer Engineering)
            Last_Login=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)
        )
        user_student1.set_password("student123")

        user_student2 = User(
            Username="rohan",
            Role="Student",
            Email="rohan.patil@kkwagh.edu.in",
            Student_ID=created_students[1].Student_ID,  # Rohan Patil
            Last_Login=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
        )
        user_student2.set_password("student123")

        user_student3 = User(
            Username="snehal",
            Role="Student",
            Email="snehal.deshmukh@kkwagh.edu.in",
            Student_ID=created_students[2].Student_ID,  # Snehal Deshmukh
            Last_Login=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2)
        )
        user_student3.set_password("student123")

        db.session.add_all([user_admin, user_staff, user_exam, user_student1, user_student2, user_student3])
        db.session.flush()

        # ---------------------------------------------------------------------
        # 7. Sample Certificate Document
        # ---------------------------------------------------------------------
        sample_cert_dir = app.config['CERTIFICATES_FOLDER']
        os.makedirs(sample_cert_dir, exist_ok=True)
        sample_file_path = os.path.join(sample_cert_dir, "sample_btech_degree_kkw.pdf")
        if not os.path.exists(sample_file_path):
            with open(sample_file_path, "wb") as f:
                f.write(b"%PDF-1.4\n% EduDesk - KKWIEER Autonomous Engineering Degree Document\n%%EOF")

        # ---------------------------------------------------------------------
        # 8. Engineering Certificates (26)
        # ---------------------------------------------------------------------
        certs_specs = [
            # 1. Aditi Shinde - Active B.Tech Degree
            ("KKW-2025-00001", "B.Tech Degree in Computer Engineering", created_students[0].Student_ID, type_degree.Type_ID, auth_dir.Authority_ID, datetime.date(2025, 6, 20), None, "Active", "Distinction (CGPA 9.62)"),
            # 2. Aditi Shinde - Active Merit Award
            ("KKW-2025-00002", "Institute Gold Medal - Academic Excellence in Computer Engineering", created_students[0].Student_ID, type_symposium.Type_ID, auth_dir.Authority_ID, datetime.date(2025, 6, 25), None, "Active", "Outstanding (Rank 1)"),
            # 3. Rohan Patil - Active B.Tech Degree
            ("KKW-2025-00003", "B.Tech Degree in Computer Engineering", created_students[1].Student_ID, type_degree.Type_ID, auth_dir.Authority_ID, datetime.date(2025, 6, 20), None, "Active", "First Class (CGPA 8.84)"),
            # 4. Snehal Deshmukh - Active B.Tech Degree
            ("KKW-2025-00004", "B.Tech Degree in Information Technology", created_students[2].Student_ID, type_degree.Type_ID, auth_dir.Authority_ID, datetime.date(2025, 6, 20), None, "Active", "Distinction (CGPA 9.12)"),
            # 5. Pranav Kulkarni - Active Honors
            ("KKW-2025-00005", "Honors Specialization in Cloud Computing & Cybersecurity", created_students[3].Student_ID, type_honors.Type_ID, auth_coe.Authority_ID, datetime.date(2025, 6, 22), None, "Active", "Distinction (CGPA 9.05)"),
            # 6. Neha Sharma - Active B.Tech Degree
            ("KKW-2025-00006", "B.Tech Degree in Electronics & Telecommunication", created_students[4].Student_ID, type_degree.Type_ID, auth_dir.Authority_ID, datetime.date(2025, 6, 20), None, "Active", "First Class (CGPA 8.75)"),
            # 7. Aditya Joshi - Active Capstone Project
            ("KKW-2025-00007", "Capstone Project: Autonomous Drone Navigation using Deep RL", created_students[5].Student_ID, type_project.Type_ID, auth_coe.Authority_ID, datetime.date(2025, 5, 15), None, "Active", "Grade A+ (Excellent)"),
            # 8. Pooja Gaikwad - REVOKED Degree
            ("KKW-2025-00008", "B.Tech Degree in Computer Engineering", created_students[6].Student_ID, type_degree.Type_ID, auth_dir.Authority_ID, datetime.date(2025, 6, 20), None, "Revoked", "First Class"),
            # 9. Sanket Wagh - Active B.Tech Degree
            ("KKW-2025-00009", "B.Tech Degree in Information Technology", created_students[7].Student_ID, type_degree.Type_ID, auth_dir.Authority_ID, datetime.date(2025, 6, 20), None, "Active", "First Class (CGPA 8.60)"),
            # 10. Tanvi More - Active B.Tech Degree
            ("KKW-2025-00010", "B.Tech Degree in Electronics & Telecommunication", created_students[8].Student_ID, type_degree.Type_ID, auth_dir.Authority_ID, datetime.date(2025, 6, 20), None, "Active", "Distinction (CGPA 9.20)"),
            # 11. Yash Bhamare - Active Hackathon Award
            ("KKW-2025-00011", "National Winner - Smart India Hackathon (SIH)", created_students[9].Student_ID, type_symposium.Type_ID, auth_dir.Authority_ID, datetime.date(2024, 12, 22), None, "Active", "1st Prize Winner"),
            # 12. Aditi Shinde - EXPIRED Course Certification
            ("KKW-2023-00012", "Distributed Systems & Kubernetes Hands-on Workshop", created_students[0].Student_ID, type_transcript.Type_ID, auth_coe.Authority_ID, datetime.date(2023, 1, 15), datetime.date(2024, 1, 15), "Expired", "Grade A"),
            # 13. Rohan Patil - EXPIRED Cybersecurity Training
            ("KKW-2023-00013", "Certified Threat Intelligence & Network Security Specialist", created_students[1].Student_ID, type_transcript.Type_ID, auth_coe.Authority_ID, datetime.date(2023, 3, 30), datetime.date(2024, 3, 30), "Expired", "Grade A+"),
            # 14. Snehal Deshmukh - REVOKED Internship
            ("KKW-2024-00014", "Corporate Industrial Internship at Tata Consultancy Services (TCS)", created_students[2].Student_ID, type_internship.Type_ID, auth_tnp.Authority_ID, datetime.date(2024, 2, 1), datetime.date(2026, 2, 1), "Revoked", "Satisfactory"),
            # 15. Aditya Joshi - EXPIRED Cloud Certification
            ("KKW-2023-00015", "Google Cloud Associate Cloud Engineer Training", created_students[5].Student_ID, type_transcript.Type_ID, auth_coe.Authority_ID, datetime.date(2023, 5, 20), datetime.date(2024, 5, 20), "Expired", "Grade A"),
            # 16. Sakshi Kale - Active Mechanical Degree
            ("KKW-2025-00016", "B.Tech Degree in Mechanical Engineering", created_students[10].Student_ID, type_degree.Type_ID, auth_dir.Authority_ID, datetime.date(2025, 6, 20), None, "Active", "Distinction (CGPA 9.35)"),
            # 17. Omkar Shinde - Active Mechanical Degree
            ("KKW-2025-00017", "B.Tech Degree in Mechanical Engineering", created_students[11].Student_ID, type_degree.Type_ID, auth_dir.Authority_ID, datetime.date(2025, 6, 20), None, "Active", "First Class (CGPA 8.70)"),
            # 18. Shruti Jagtap - Active Civil Degree
            ("KKW-2025-00018", "B.Tech Degree in Civil Engineering", created_students[12].Student_ID, type_degree.Type_ID, auth_dir.Authority_ID, datetime.date(2025, 6, 20), None, "Active", "Distinction (CGPA 9.40)"),
            # 19. Tejas Bagul - REVOKED Civil Degree
            ("KKW-2025-00019", "B.Tech Degree in Civil Engineering", created_students[13].Student_ID, type_degree.Type_ID, auth_dir.Authority_ID, datetime.date(2025, 6, 20), None, "Revoked", "Pass Class"),
            # 20. Rutuja Nikam - Active AI & Data Science Degree
            ("KKW-2025-00020", "B.Tech Degree in AI & Data Science", created_students[14].Student_ID, type_degree.Type_ID, auth_dir.Authority_ID, datetime.date(2025, 6, 20), None, "Active", "Distinction (CGPA 9.55)"),
            # 21. Sahil Sonawane - Active AI & Data Science Degree
            ("KKW-2025-00021", "B.Tech Degree in AI & Data Science", created_students[15].Student_ID, type_degree.Type_ID, auth_dir.Authority_ID, datetime.date(2025, 6, 20), None, "Active", "First Class (CGPA 8.90)"),
            # 22. Mansi Wagh - Active VLSI Honors
            ("KKW-2025-00022", "Honors in VLSI Design & Embedded System Architectures", created_students[16].Student_ID, type_honors.Type_ID, auth_coe.Authority_ID, datetime.date(2025, 6, 22), None, "Active", "Distinction (CGPA 9.25)"),
            # 23. Kunal Khairnar - Active Robotics Minor
            ("KKW-2025-00023", "Minor Degree in Robotics & Industrial Automation", created_students[17].Student_ID, type_honors.Type_ID, auth_coe.Authority_ID, datetime.date(2025, 6, 22), None, "Active", "First Class (CGPA 8.80)"),
            # 24. Neha Gangurde - EXPIRED Siemens Internship
            ("KKW-2023-00024", "6-Month Industrial Engineering Internship at Siemens India", created_students[18].Student_ID, type_internship.Type_ID, auth_tnp.Authority_ID, datetime.date(2023, 7, 1), datetime.date(2024, 7, 1), "Expired", "Outstanding"),
            # 25. Parth Salunke - EXPIRED Bosch Training
            ("KKW-2023-00025", "Advanced Computer Vision & Autonomous Systems Training", created_students[19].Student_ID, type_transcript.Type_ID, auth_coe.Authority_ID, datetime.date(2023, 8, 15), datetime.date(2024, 8, 15), "Expired", "Grade A+"),
            # 26. Aditi Shinde - Active DSA Engineering Credential (user created)
            ("KKW-2026-00026", "Data Structures & Algorithms (DSA) Engineering Certification", created_students[0].Student_ID, type_transcript.Type_ID, auth_coe.Authority_ID, datetime.date(2026, 10, 27), None, "Active", "Distinction")
        ]

        created_certs = []
        for spec in certs_specs:
            cert_no = spec[0]
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
                Certificate_File="uploads/certificates/sample_btech_degree_kkw.pdf"
            )
            db.session.add(cert)
            db.session.flush()
            created_certs.append(cert)

        # ---------------------------------------------------------------------
        # 9. Revocations (WEAK Entity: Composite PK (Certificate_ID, Revocation_No))
        # ---------------------------------------------------------------------
        rev_1 = Revocation(
            Certificate_ID=created_certs[7].Certificate_ID,
            Revocation_No=1,
            Reason="Falsified prerequisite credit submissions; autonomous inquiry committee order #KKW/ENGR/DISC-2025/08",
            Revoked_Date=datetime.date(2025, 7, 10),
            User_ID=user_admin.User_ID
        )

        rev_2 = Revocation(
            Certificate_ID=created_certs[13].Certificate_ID,
            Revocation_No=1,
            Reason="Administrative recall: candidate failed to fulfill mandatory 120-day in-plant industrial internship attendance",
            Revoked_Date=datetime.date(2025, 8, 15),
            User_ID=user_staff.User_ID
        )

        rev_3 = Revocation(
            Certificate_ID=created_certs[18].Certificate_ID,
            Revocation_No=1,
            Reason="Plagiarism detected in final capstone design thesis exceeding statutory AICTE threshold limit",
            Revoked_Date=datetime.date(2025, 9, 2),
            User_ID=user_exam.User_ID
        )
        db.session.add_all([rev_1, rev_2, rev_3])

        # ---------------------------------------------------------------------
        # 10. Audit Logs
        # ---------------------------------------------------------------------
        sample_logs = [
            AuditLog(Action="System Initialized with Master KKWIEER Autonomous Engineering Schema", Timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7), IP_Address="127.0.0.1", User_ID=user_admin.User_ID),
            AuditLog(Action="Configured Engineering Department 'Computer Engineering'", Timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=6, hours=5), IP_Address="127.0.0.1", User_ID=user_admin.User_ID),
            AuditLog(Action="Configured Engineering Department 'Mechanical Engineering'", Timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=6, hours=4), IP_Address="127.0.0.1", User_ID=user_admin.User_ID),
            AuditLog(Action="Configured Engineering Department 'Artificial Intelligence & Data Science'", Timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=6, hours=3), IP_Address="127.0.0.1", User_ID=user_admin.User_ID),
            AuditLog(Action="Registered engineering student 'Aditi Shinde' (2021BTECS001)", Timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=5, hours=2), IP_Address="127.0.0.1", User_ID=user_staff.User_ID),
            AuditLog(Action="Registered engineering student 'Sakshi Kale' (2021BTME011)", Timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=5, hours=1), IP_Address="127.0.0.1", User_ID=user_staff.User_ID),
            AuditLog(Action="Issued certificate KKW-2025-00001 (B.Tech Degree) to student 2021BTECS001", Timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=4, hours=8), IP_Address="127.0.0.1", User_ID=user_staff.User_ID),
            AuditLog(Action="Issued certificate KKW-2025-00016 (B.Tech Mechanical) to student 2021BTME011", Timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=4, hours=6), IP_Address="127.0.0.1", User_ID=user_exam.User_ID),
            AuditLog(Action="Revoked certificate KKW-2025-00008 (Reason: Disciplinary Committee Order)", Timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3, hours=2), IP_Address="127.0.0.1", User_ID=user_admin.User_ID),
            AuditLog(Action="Revoked certificate KKW-2025-00019 (Reason: Thesis Plagiarism)", Timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2, hours=4), IP_Address="127.0.0.1", User_ID=user_exam.User_ID),
            AuditLog(Action="Login successful for user 'admin'", Timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2), IP_Address="127.0.0.1", User_ID=user_admin.User_ID),
            AuditLog(Action="Login successful for user 'staff'", Timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1), IP_Address="127.0.0.1", User_ID=user_staff.User_ID),
            AuditLog(Action="Public Verification Query: KKW-2025-00001 (Result: Found)", Timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=45), IP_Address="192.168.1.15", User_ID=user_admin.User_ID),
            AuditLog(Action="Public Verification Query: KKW-2025-00008 (Result: Revoked)", Timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=20), IP_Address="192.168.1.42", User_ID=user_admin.User_ID)
        ]
        db.session.add_all(sample_logs)

        # ---------------------------------------------------------------------
        # 11. Notifications
        # ---------------------------------------------------------------------
        sample_notifs = [
            Notification(Message="Welcome to EduDesk KKWIEER Portal! Administrative controls initialized.", Sent_Date=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=5), Status="Read", User_ID=user_admin.User_ID),
            Notification(Message="Staff permissions configured for Engineering Student Credentials.", Sent_Date=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=4), Status="Read", User_ID=user_staff.User_ID),
            Notification(Message="Autonomous Examination Section access authorized for B.Tech convocation grade releases.", Sent_Date=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3), Status="Read", User_ID=user_exam.User_ID),
            Notification(Message="Your credential 'B.Tech Degree in Computer Engineering' (KKW-2025-00001) has been issued.", Sent_Date=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2), Status="Unread", User_ID=user_student1.User_ID),
            Notification(Message="Your credential 'Institute Gold Medal - Academic Excellence' (KKW-2025-00002) has been issued.", Sent_Date=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=12), Status="Unread", User_ID=user_student1.User_ID),
            Notification(Message="Course Certification 'Distributed Systems Workshop' (KKW-2023-00012) has reached validity expiration.", Sent_Date=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=4), Status="Unread", User_ID=user_student1.User_ID),
            Notification(Message="Your credential 'B.Tech Degree in Computer Engineering' (KKW-2025-00003) has been issued.", Sent_Date=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2), Status="Unread", User_ID=user_student2.User_ID),
            Notification(Message="Your credential 'B.Tech Degree in Information Technology' (KKW-2025-00004) has been issued.", Sent_Date=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2), Status="Unread", User_ID=user_student3.User_ID)
        ]
        db.session.add_all(sample_notifs)

        db.session.commit()
        print("✅ Database successfully seeded with 100% Engineering data for KKWIEER Nashik:")
        print("   - 6 Engineering Departments, 10 B.Tech/M.Tech Degree Courses")
        print("   - 6 Engineering Certificate Categories, 3 Autonomous Issuing Authorities (6 phone numbers)")
        print("   - 20 Engineering Undergrad Students (PRN/Enrollment format, 21 phone numbers)")
        print("   - 6 Users: Admin, Staff, CoE, and Students (Aditi Shinde, Rohan, Snehal)")
        print("   - 26 Engineering Certificates: Degrees, Capstones, Internships, Hackathons (18 Active, 5 Expired, 3 Revoked)")
        print("   - 3 Revocation records (weak entity with composite PK)")
        print("   - 14 Audit Logs and 8 Notifications")

if __name__ == '__main__':
    seed_database()
