import re
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Student, StudentPhone, Department, Course, Certificate
from utils.decorators import role_required, get_current_student
from utils.audit import log_audit

students_bp = Blueprint('students', __name__, url_prefix='/students')

PHONE_REGEX = re.compile(r'^\+?[0-9]{10,15}$')
PINCODE_REGEX = re.compile(r'^[0-9]{6}$')

@students_bp.route('/')
@login_required
@role_required(['Admin', 'Staff'])
def index():
    search = request.args.get('search', '').strip()
    dept_id = request.args.get('department_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Student.query.join(Department).join(Course)
    if search:
        query = query.filter(
            (Student.First_Name.ilike(f'%{search}%')) |
            (Student.Last_Name.ilike(f'%{search}%')) |
            (Student.Enrollment_No.ilike(f'%{search}%')) |
            (Student.Email.ilike(f'%{search}%')) |
            (Department.Department_Name.ilike(f'%{search}%')) |
            (Course.Course_Name.ilike(f'%{search}%'))
        )
    if dept_id:
        query = query.filter(Student.Department_ID == dept_id)

    pagination = query.order_by(Student.Student_ID.desc()).paginate(page=page, per_page=per_page, error_out=False)
    students = pagination.items
    departments = Department.query.order_by(Department.Department_Name.asc()).all()

    return render_template(
        'students/index.html',
        students=students,
        pagination=pagination,
        search=search,
        selected_dept_id=dept_id,
        departments=departments
    )


@students_bp.route('/profile')
@login_required
def profile():
    """View personal profile for logged-in student."""
    if not current_user.is_student:
        flash("Profile view is designated for student accounts.", "info")
        return redirect(url_for('dashboard.index'))

    student = get_current_student()
    if not student:
        flash("No student profile linked to your user account. Please contact the administrator.", "warning")
        return redirect(url_for('dashboard.index'))

    certificates = Certificate.query.filter_by(Student_ID=student.Student_ID).order_by(Certificate.Issue_Date.desc()).all()
    return render_template('students/profile.html', student=student, certificates=certificates)


@students_bp.route('/<int:id>')
@login_required
def detail(id):
    """View details of a student."""
    if current_user.is_student:
        # Students can only view their own record
        student = get_current_student()
        if not student or student.Student_ID != id:
            abort(403)
    else:
        student = Student.query.get_or_404(id)

    certificates = Certificate.query.filter_by(Student_ID=student.Student_ID).order_by(Certificate.Issue_Date.desc()).all()
    return render_template('students/profile.html', student=student, certificates=certificates)


@students_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def add():
    departments = Department.query.order_by(Department.Department_Name.asc()).all()
    courses = Course.query.order_by(Course.Course_Name.asc()).all()

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        enroll_no = request.form.get('enrollment_no', '').strip()
        dob_str = request.form.get('dob', '').strip()
        batch_year = request.form.get('batch_year', type=int)
        house_no = request.form.get('house_no', '').strip()
        street = request.form.get('street', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        dept_id = request.form.get('department_id', type=int)
        course_id = request.form.get('course_id', type=int)
        phones = request.form.getlist('phones[]')

        if not first_name or not enroll_no:
            flash('First Name and Enrollment Number are required.', 'danger')
            return render_template('students/form.html', action='Add', student=None, departments=departments, courses=courses, phones=phones)

        if not dept_id or not Department.query.get(dept_id):
            flash('Please select a valid Department.', 'danger')
            return render_template('students/form.html', action='Add', student=None, departments=departments, courses=courses, phones=phones)

        if not course_id or not Course.query.get(course_id):
            flash('Please select a valid Course.', 'danger')
            return render_template('students/form.html', action='Add', student=None, departments=departments, courses=courses, phones=phones)

        if pincode and not PINCODE_REGEX.match(pincode):
            flash('Pincode must be exactly 6 digits.', 'danger')
            return render_template('students/form.html', action='Add', student=None, departments=departments, courses=courses, phones=phones)

        # Unique checks
        if Student.query.filter_by(Enrollment_No=enroll_no).first():
            flash(f"Student with Enrollment Number '{enroll_no}' already exists.", 'danger')
            return render_template('students/form.html', action='Add', student=None, departments=departments, courses=courses, phones=phones)

        if email and Student.query.filter_by(Email=email).first():
            flash(f"Student with Email '{email}' already exists.", 'danger')
            return render_template('students/form.html', action='Add', student=None, departments=departments, courses=courses, phones=phones)

        # Parse DOB
        dob = None
        if dob_str:
            try:
                dob = datetime.datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid Date of Birth format. Please use YYYY-MM-DD.', 'danger')
                return render_template('students/form.html', action='Add', student=None, departments=departments, courses=courses, phones=phones)

        # Validate phones
        valid_phones = []
        for p in phones:
            p_clean = p.strip()
            if p_clean:
                if not PHONE_REGEX.match(p_clean):
                    flash(f"Invalid phone number '{p_clean}'. Must be 10 to 15 digits.", 'danger')
                    return render_template('students/form.html', action='Add', student=None, departments=departments, courses=courses, phones=phones)
                if p_clean not in valid_phones:
                    valid_phones.append(p_clean)

        student = Student(
            First_Name=first_name,
            Last_Name=last_name or None,
            Email=email or None,
            Enrollment_No=enroll_no,
            Date_of_Birth=dob,
            Batch_Year=batch_year or None,
            House_no=house_no or None,
            Street=street or None,
            City=city or None,
            State=state or None,
            Pincode=pincode or None,
            Department_ID=dept_id,
            Course_ID=course_id
        )
        db.session.add(student)
        db.session.flush()

        for p in valid_phones:
            db.session.add(StudentPhone(Student_ID=student.Student_ID, Phone_No=p))

        try:
            db.session.commit()
            log_audit(f"Created student: {student.full_name} ({student.Enrollment_No})")
            flash(f"Student '{student.full_name}' added successfully!", 'success')
            return redirect(url_for('students.index'))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred. Check that Enrollment Number and Email are unique.", 'danger')

    return render_template('students/form.html', action='Add', student=None, departments=departments, courses=courses, phones=[])


@students_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def edit(id):
    student = Student.query.get_or_404(id)
    departments = Department.query.order_by(Department.Department_Name.asc()).all()
    courses = Course.query.order_by(Course.Course_Name.asc()).all()

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        enroll_no = request.form.get('enrollment_no', '').strip()
        dob_str = request.form.get('dob', '').strip()
        batch_year = request.form.get('batch_year', type=int)
        house_no = request.form.get('house_no', '').strip()
        street = request.form.get('street', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        dept_id = request.form.get('department_id', type=int)
        course_id = request.form.get('course_id', type=int)
        phones = request.form.getlist('phones[]')

        if not first_name or not enroll_no:
            flash('First Name and Enrollment Number are required.', 'danger')
            return render_template('students/form.html', action='Edit', student=student, departments=departments, courses=courses, phones=phones)

        if not dept_id or not Department.query.get(dept_id):
            flash('Please select a valid Department.', 'danger')
            return render_template('students/form.html', action='Edit', student=student, departments=departments, courses=courses, phones=phones)

        if not course_id or not Course.query.get(course_id):
            flash('Please select a valid Course.', 'danger')
            return render_template('students/form.html', action='Edit', student=student, departments=departments, courses=courses, phones=phones)

        if pincode and not PINCODE_REGEX.match(pincode):
            flash('Pincode must be exactly 6 digits.', 'danger')
            return render_template('students/form.html', action='Edit', student=student, departments=departments, courses=courses, phones=phones)

        # Unique checks against others
        existing_enroll = Student.query.filter(Student.Enrollment_No == enroll_no, Student.Student_ID != id).first()
        if existing_enroll:
            flash(f"Enrollment Number '{enroll_no}' already exists.", 'danger')
            return render_template('students/form.html', action='Edit', student=student, departments=departments, courses=courses, phones=phones)

        if email:
            existing_email = Student.query.filter(Student.Email == email, Student.Student_ID != id).first()
            if existing_email:
                flash(f"Email '{email}' already exists.", 'danger')
                return render_template('students/form.html', action='Edit', student=student, departments=departments, courses=courses, phones=phones)

        dob = None
        if dob_str:
            try:
                dob = datetime.datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid Date of Birth format. Please use YYYY-MM-DD.', 'danger')
                return render_template('students/form.html', action='Edit', student=student, departments=departments, courses=courses, phones=phones)

        valid_phones = []
        for p in phones:
            p_clean = p.strip()
            if p_clean:
                if not PHONE_REGEX.match(p_clean):
                    flash(f"Invalid phone number '{p_clean}'. Must be 10 to 15 digits.", 'danger')
                    return render_template('students/form.html', action='Edit', student=student, departments=departments, courses=courses, phones=phones)
                if p_clean not in valid_phones:
                    valid_phones.append(p_clean)

        student.First_Name = first_name
        student.Last_Name = last_name or None
        student.Email = email or None
        student.Enrollment_No = enroll_no
        student.Date_of_Birth = dob
        student.Batch_Year = batch_year or None
        student.House_no = house_no or None
        student.Street = street or None
        student.City = city or None
        student.State = state or None
        student.Pincode = pincode or None
        student.Department_ID = dept_id
        student.Course_ID = course_id

        # Update phones
        StudentPhone.query.filter_by(Student_ID=id).delete()
        for p in valid_phones:
            db.session.add(StudentPhone(Student_ID=id, Phone_No=p))

        try:
            db.session.commit()
            log_audit(f"Updated student: {student.full_name} ({student.Enrollment_No})")
            flash(f"Student '{student.full_name}' updated successfully!", 'success')
            return redirect(url_for('students.index'))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred while updating student record.", 'danger')

    current_phones = [p.Phone_No for p in student.phones]
    return render_template('students/form.html', action='Edit', student=student, departments=departments, courses=courses, phones=current_phones)


@students_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required(['Admin'])  # Only Admin can delete; Staff is blocked
def delete(id):
    student = Student.query.get_or_404(id)
    student_name = student.full_name

    # Check for certificates (RESTRICT constraint)
    if student.certificates and len(student.certificates) > 0:
        flash(f"Cannot delete student '{student_name}': student has {len(student.certificates)} associated certificates.", 'danger')
        return redirect(url_for('students.index'))

    try:
        db.session.delete(student)
        db.session.commit()
        log_audit(f"Deleted student: {student_name}")
        flash(f"Student '{student_name}' deleted successfully.", 'success')
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete student '{student_name}': record is referenced by other database records.", 'danger')

    return redirect(url_for('students.index'))
