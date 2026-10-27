import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db, login_manager

# -----------------------------------------------------------------------------
# User Loader for Flask-Login
# -----------------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -----------------------------------------------------------------------------
# Table 5.1: Department
# -----------------------------------------------------------------------------
class Department(db.Model):
    __tablename__ = 'Department'

    Department_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Department_Name = db.Column(db.String(100), nullable=False, unique=True)
    HOD_Name = db.Column(db.String(100))
    Email = db.Column(db.String(100), unique=True)

    # Relationships
    courses = db.relationship('Course', backref='department', lazy=True)
    students = db.relationship('Student', backref='department', lazy=True)

    def __repr__(self):
        return f"<Department {self.Department_Name}>"


# -----------------------------------------------------------------------------
# Table 5.2: Course
# -----------------------------------------------------------------------------
class Course(db.Model):
    __tablename__ = 'Course'

    Course_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Course_Name = db.Column(db.String(100), nullable=False)
    Duration = db.Column(db.String(30))
    Department_ID = db.Column(
        db.Integer,
        db.ForeignKey('Department.Department_ID', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False
    )

    # Relationships
    students = db.relationship('Student', backref='course', lazy=True)

    def __repr__(self):
        return f"<Course {self.Course_Name}>"


# -----------------------------------------------------------------------------
# Table 5.3: Certificate_Type
# -----------------------------------------------------------------------------
class CertificateType(db.Model):
    __tablename__ = 'Certificate_Type'

    Type_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Type_Name = db.Column(db.String(50), nullable=False, unique=True)
    Description = db.Column(db.String(255))

    # Relationships
    certificates = db.relationship('Certificate', backref='certificate_type', lazy=True)

    def __repr__(self):
        return f"<CertificateType {self.Type_Name}>"


# -----------------------------------------------------------------------------
# Table 5.4: Issuing_Authority
# -----------------------------------------------------------------------------
class IssuingAuthority(db.Model):
    __tablename__ = 'Issuing_Authority'

    Authority_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Authority_Name = db.Column(db.String(100), nullable=False)
    Registration_No = db.Column(db.String(50), unique=True)
    Email = db.Column(db.String(100))
    Website = db.Column(db.String(150))
    House_no = db.Column(db.String(20))
    Street = db.Column(db.String(100))
    City = db.Column(db.String(50))
    State = db.Column(db.String(50))
    Pincode = db.Column(db.String(6))

    # Relationships
    phones = db.relationship(
        'AuthorityPhone',
        backref='authority',
        lazy=True,
        cascade='all, delete-orphan'
    )
    certificates = db.relationship('Certificate', backref='authority', lazy=True)

    @property
    def full_address(self):
        parts = [self.House_no, self.Street, self.City, self.State, self.Pincode]
        return ", ".join([p for p in parts if p])

    def __repr__(self):
        return f"<IssuingAuthority {self.Authority_Name}>"


# -----------------------------------------------------------------------------
# Table 5.5: Authority_Phone (Composite PK)
# -----------------------------------------------------------------------------
class AuthorityPhone(db.Model):
    __tablename__ = 'Authority_Phone'

    Authority_ID = db.Column(
        db.Integer,
        db.ForeignKey('Issuing_Authority.Authority_ID', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True
    )
    Phone_No = db.Column(db.String(15), primary_key=True)

    def __repr__(self):
        return f"<AuthorityPhone {self.Authority_ID}: {self.Phone_No}>"


# -----------------------------------------------------------------------------
# Table 5.6: Student
# -----------------------------------------------------------------------------
class Student(db.Model):
    __tablename__ = 'Student'

    Student_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    First_Name = db.Column(db.String(50), nullable=False)
    Last_Name = db.Column(db.String(50))
    Email = db.Column(db.String(100), unique=True)
    Enrollment_No = db.Column(db.String(30), nullable=False, unique=True)
    Date_of_Birth = db.Column(db.Date)
    Batch_Year = db.Column(db.Integer)
    House_no = db.Column(db.String(20))
    Street = db.Column(db.String(100))
    City = db.Column(db.String(50))
    State = db.Column(db.String(50))
    Pincode = db.Column(db.String(6))
    Department_ID = db.Column(
        db.Integer,
        db.ForeignKey('Department.Department_ID', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False
    )
    Course_ID = db.Column(
        db.Integer,
        db.ForeignKey('Course.Course_ID', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False
    )

    # Relationships
    phones = db.relationship(
        'StudentPhone',
        backref='student',
        lazy=True,
        cascade='all, delete-orphan'
    )
    certificates = db.relationship('Certificate', backref='student', lazy=True)
    user_account = db.relationship('User', backref='student_profile', uselist=False, lazy=True)

    # Derived attributes (computed at runtime, NEVER stored)
    @property
    def age(self):
        if not self.Date_of_Birth:
            return None
        today = datetime.date.today()
        birth = self.Date_of_Birth
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

    @property
    def full_name(self):
        if self.Last_Name:
            return f"{self.First_Name} {self.Last_Name}"
        return self.First_Name

    @property
    def full_address(self):
        parts = [self.House_no, self.Street, self.City, self.State, self.Pincode]
        return ", ".join([p for p in parts if p])

    def __repr__(self):
        return f"<Student {self.Enrollment_No} - {self.full_name}>"


# -----------------------------------------------------------------------------
# Table 5.7: Student_Phone (Composite PK)
# -----------------------------------------------------------------------------
class StudentPhone(db.Model):
    __tablename__ = 'Student_Phone'

    Student_ID = db.Column(
        db.Integer,
        db.ForeignKey('Student.Student_ID', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True
    )
    Phone_No = db.Column(db.String(15), primary_key=True)

    def __repr__(self):
        return f"<StudentPhone {self.Student_ID}: {self.Phone_No}>"


# -----------------------------------------------------------------------------
# Table 5.8: Users
# -----------------------------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'Users'

    User_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Username = db.Column(db.String(50), nullable=False, unique=True)
    Password_Hash = db.Column(db.String(255), nullable=False)
    Role = db.Column(db.String(20), nullable=False)  # Admin, Staff, Student
    Email = db.Column(db.String(100), unique=True)
    Last_Login = db.Column(db.DateTime, nullable=True)
    Student_ID = db.Column(
        db.Integer,
        db.ForeignKey('Student.Student_ID', ondelete='SET NULL', onupdate='CASCADE'),
        nullable=True
    )

    # Relationships
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    revocations = db.relationship('Revocation', backref='user', lazy=True)

    # Flask-Login override
    def get_id(self):
        return str(self.User_ID)

    def set_password(self, password):
        self.Password_Hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.Password_Hash, password)

    @property
    def is_admin(self):
        return self.Role == 'Admin'

    @property
    def is_staff(self):
        return self.Role == 'Staff'

    @property
    def is_student(self):
        return self.Role == 'Student'

    def __repr__(self):
        return f"<User {self.Username} ({self.Role})>"


# -----------------------------------------------------------------------------
# Table 5.9: Certificate
# -----------------------------------------------------------------------------
class Certificate(db.Model):
    __tablename__ = 'Certificate'

    Certificate_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Certificate_Number = db.Column(db.String(50), nullable=False, unique=True)
    Certificate_Name = db.Column(db.String(150), nullable=False)
    Issue_Date = db.Column(db.Date, nullable=False)
    Expiry_Date = db.Column(db.Date, nullable=True)
    Status = db.Column(db.String(10), default='Active')  # Active, Expired, Revoked
    Grade = db.Column(db.String(50))
    QR_Code = db.Column(db.String(255))
    Certificate_File = db.Column(db.String(255))

    Student_ID = db.Column(
        db.Integer,
        db.ForeignKey('Student.Student_ID', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False
    )
    Type_ID = db.Column(
        db.Integer,
        db.ForeignKey('Certificate_Type.Type_ID', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False
    )
    Authority_ID = db.Column(
        db.Integer,
        db.ForeignKey('Issuing_Authority.Authority_ID', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False
    )

    # Relationships
    revocations = db.relationship(
        'Revocation',
        backref='certificate',
        lazy=True,
        cascade='all, delete-orphan',
        order_by='Revocation.Revocation_No.desc()'
    )

    @property
    def latest_revocation(self):
        if self.revocations:
            return self.revocations[0]
        return None

    def __repr__(self):
        return f"<Certificate {self.Certificate_Number} - {self.Certificate_Name}>"


# -----------------------------------------------------------------------------
# Table 5.10: Revocation (WEAK Entity, Composite PK)
# -----------------------------------------------------------------------------
class Revocation(db.Model):
    __tablename__ = 'Revocation'

    Certificate_ID = db.Column(
        db.Integer,
        db.ForeignKey('Certificate.Certificate_ID', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True
    )
    Revocation_No = db.Column(db.Integer, primary_key=True)
    Reason = db.Column(db.String(500), nullable=False)
    Revoked_Date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    User_ID = db.Column(
        db.Integer,
        db.ForeignKey('Users.User_ID', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False
    )

    def __repr__(self):
        return f"<Revocation Cert:{self.Certificate_ID} No:{self.Revocation_No}>"


# -----------------------------------------------------------------------------
# Table 5.11: Audit_Log
# -----------------------------------------------------------------------------
class AuditLog(db.Model):
    __tablename__ = 'Audit_Log'

    Log_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Action = db.Column(db.String(255), nullable=False)
    Timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    IP_Address = db.Column(db.String(45))
    User_ID = db.Column(
        db.Integer,
        db.ForeignKey('Users.User_ID', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False
    )

    def __repr__(self):
        return f"<AuditLog {self.Action} by User {self.User_ID} at {self.Timestamp}>"


# -----------------------------------------------------------------------------
# Table 5.12: Notification
# -----------------------------------------------------------------------------
class Notification(db.Model):
    __tablename__ = 'Notification'

    Notification_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Message = db.Column(db.Text, nullable=False)
    Sent_Date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    Status = db.Column(db.String(15), default='Unread')  # Unread, Read
    User_ID = db.Column(
        db.Integer,
        db.ForeignKey('Users.User_ID', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )

    def __repr__(self):
        return f"<Notification {self.Notification_ID} for User {self.User_ID} [{self.Status}]>"
