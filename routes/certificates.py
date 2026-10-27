import os
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_from_directory, current_app
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Certificate, Student, CertificateType, IssuingAuthority, Revocation, User
from utils.decorators import role_required, get_current_student
from utils.helpers import save_uploaded_certificate
from utils.qr_generator import generate_certificate_qr
from utils.audit import log_audit
from utils.notifications import notify_student_certificate, notify_admins
from utils.expiry import check_and_update_expired_certificates

certificates_bp = Blueprint('certificates', __name__, url_prefix='/certificates')

def generate_unique_cert_number():
    """Auto-generate a professional unique certificate number: KKW-YYYY-XXXXX"""
    year = datetime.date.today().year
    count = Certificate.query.count() + 1
    candidate = f"KKW-{year}-{count:05d}"
    while Certificate.query.filter_by(Certificate_Number=candidate).first():
        count += 1
        candidate = f"KKW-{year}-{count:05d}"
    return candidate


@certificates_bp.route('/')
@login_required
def index():
    check_and_update_expired_certificates()

    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    type_id = request.args.get('type_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Certificate.query.join(Student).join(CertificateType).join(IssuingAuthority)

    # Student isolation: Students must NEVER see other students' certificates!
    if current_user.is_student:
        student = get_current_student()
        if not student:
            flash("No student profile linked to your user account.", "warning")
            return render_template('certificates/index.html', certificates=[], pagination=None, search='', status_filter='', type_id=None, cert_types=[])
        query = query.filter(Certificate.Student_ID == student.Student_ID)

    if search:
        query = query.filter(
            (Certificate.Certificate_Number.ilike(f'%{search}%')) |
            (Certificate.Certificate_Name.ilike(f'%{search}%')) |
            (Student.First_Name.ilike(f'%{search}%')) |
            (Student.Last_Name.ilike(f'%{search}%')) |
            (Student.Enrollment_No.ilike(f'%{search}%')) |
            (IssuingAuthority.Authority_Name.ilike(f'%{search}%'))
        )

    if status_filter:
        query = query.filter(Certificate.Status == status_filter)

    if type_id:
        query = query.filter(Certificate.Type_ID == type_id)

    pagination = query.order_by(Certificate.Certificate_ID.desc()).paginate(page=page, per_page=per_page, error_out=False)
    certificates = pagination.items
    cert_types = CertificateType.query.order_by(CertificateType.Type_Name.asc()).all()

    return render_template(
        'certificates/index.html',
        certificates=certificates,
        pagination=pagination,
        search=search,
        status_filter=status_filter,
        type_id=type_id,
        cert_types=cert_types
    )


@certificates_bp.route('/<int:id>')
@login_required
def detail(id):
    cert = Certificate.query.get_or_404(id)

    # Student authorization check
    if current_user.is_student:
        student = get_current_student()
        if not student or cert.Student_ID != student.Student_ID:
            abort(403)

    return render_template('certificates/detail.html', cert=cert)


@certificates_bp.route('/<int:id>/print')
@login_required
def print_view(id):
    cert = Certificate.query.get_or_404(id)

    if current_user.is_student:
        student = get_current_student()
        if not student or cert.Student_ID != student.Student_ID:
            abort(403)

    return render_template('certificates/print.html', cert=cert)


@certificates_bp.route('/<int:id>/download')
@login_required
def download(id):
    cert = Certificate.query.get_or_404(id)

    if current_user.is_student:
        student = get_current_student()
        if not student or cert.Student_ID != student.Student_ID:
            abort(403)

    if not cert.Certificate_File:
        flash("No physical certificate file was uploaded for this certificate.", "warning")
        return redirect(url_for('certificates.detail', id=id))

    static_dir = os.path.join(current_app.root_path, 'static')
    file_path = os.path.join(static_dir, cert.Certificate_File)
    if not os.path.exists(file_path):
        flash("Certificate file not found on server.", "danger")
        return redirect(url_for('certificates.detail', id=id))

    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    return send_from_directory(directory, filename, as_attachment=True)


@certificates_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def add():
    students = Student.query.order_by(Student.First_Name.asc()).all()
    types = CertificateType.query.order_by(CertificateType.Type_Name.asc()).all()
    authorities = IssuingAuthority.query.order_by(IssuingAuthority.Authority_Name.asc()).all()
    suggested_cert_no = generate_unique_cert_number()

    if request.method == 'POST':
        cert_no = request.form.get('certificate_number', '').strip() or suggested_cert_no
        cert_name = request.form.get('certificate_name', '').strip()
        issue_date_str = request.form.get('issue_date', '').strip()
        expiry_date_str = request.form.get('expiry_date', '').strip()
        grade = request.form.get('grade', '').strip()
        student_id = request.form.get('student_id', type=int)
        type_id = request.form.get('type_id', type=int)
        authority_id = request.form.get('authority_id', type=int)
        cert_file = request.files.get('certificate_file')

        if not cert_name or not cert_no or not issue_date_str:
            flash('Certificate Number, Name, and Issue Date are required.', 'danger')
            return render_template('certificates/form.html', action='Add', cert=None, students=students, types=types, authorities=authorities, suggested_no=suggested_cert_no)

        if not student_id or not Student.query.get(student_id):
            flash('Please select a valid Student.', 'danger')
            return render_template('certificates/form.html', action='Add', cert=None, students=students, types=types, authorities=authorities, suggested_no=suggested_cert_no)

        if not type_id or not CertificateType.query.get(type_id):
            flash('Please select a valid Certificate Type.', 'danger')
            return render_template('certificates/form.html', action='Add', cert=None, students=students, types=types, authorities=authorities, suggested_no=suggested_cert_no)

        if not authority_id or not IssuingAuthority.query.get(authority_id):
            flash('Please select a valid Issuing Authority.', 'danger')
            return render_template('certificates/form.html', action='Add', cert=None, students=students, types=types, authorities=authorities, suggested_no=suggested_cert_no)

        # Unique Certificate Number check
        if Certificate.query.filter_by(Certificate_Number=cert_no).first():
            flash(f"Certificate Number '{cert_no}' is already in use.", 'danger')
            return render_template('certificates/form.html', action='Add', cert=None, students=students, types=types, authorities=authorities, suggested_no=suggested_cert_no)

        # Parse dates
        try:
            issue_date = datetime.datetime.strptime(issue_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid Issue Date format. Use YYYY-MM-DD.', 'danger')
            return render_template('certificates/form.html', action='Add', cert=None, students=students, types=types, authorities=authorities, suggested_no=suggested_cert_no)

        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
                if expiry_date < issue_date:
                    flash('Expiry Date must be greater than or equal to Issue Date.', 'danger')
                    return render_template('certificates/form.html', action='Add', cert=None, students=students, types=types, authorities=authorities, suggested_no=suggested_cert_no)
            except ValueError:
                flash('Invalid Expiry Date format. Use YYYY-MM-DD.', 'danger')
                return render_template('certificates/form.html', action='Add', cert=None, students=students, types=types, authorities=authorities, suggested_no=suggested_cert_no)

        # Determine initial status
        today = datetime.date.today()
        status = 'Active'
        if expiry_date and expiry_date < today:
            status = 'Expired'

        # File upload
        file_path = None
        if cert_file and cert_file.filename:
            file_path = save_uploaded_certificate(cert_file)
            if not file_path:
                flash('Invalid file upload. Allowed types: PDF, PNG, JPG, JPEG.', 'danger')
                return render_template('certificates/form.html', action='Add', cert=None, students=students, types=types, authorities=authorities, suggested_no=suggested_cert_no)

        # Generate QR code linking to public verification page
        # Encode full URL or path
        qr_code_path = generate_certificate_qr(cert_no, f"/verify/{cert_no}")

        cert = Certificate(
            Certificate_Number=cert_no,
            Certificate_Name=cert_name,
            Issue_Date=issue_date,
            Expiry_Date=expiry_date,
            Status=status,
            Grade=grade or None,
            QR_Code=qr_code_path,
            Certificate_File=file_path,
            Student_ID=student_id,
            Type_ID=type_id,
            Authority_ID=authority_id
        )
        db.session.add(cert)
        try:
            db.session.commit()
            log_audit(f"Issued certificate: {cert.Certificate_Number} - {cert.Certificate_Name}")

            # Notify the student
            notify_student_certificate(
                student_id,
                f"Your certificate '{cert.Certificate_Name}' ({cert.Certificate_Number}) has been issued."
            )

            flash(f"Certificate '{cert.Certificate_Number}' issued successfully!", 'success')
            return redirect(url_for('certificates.detail', id=cert.Certificate_ID))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred while creating the certificate. Verify uniqueness of Certificate Number.", 'danger')

    return render_template('certificates/form.html', action='Add', cert=None, students=students, types=types, authorities=authorities, suggested_no=suggested_cert_no)


@certificates_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def edit(id):
    cert = Certificate.query.get_or_404(id)
    students = Student.query.order_by(Student.First_Name.asc()).all()
    types = CertificateType.query.order_by(CertificateType.Type_Name.asc()).all()
    authorities = IssuingAuthority.query.order_by(IssuingAuthority.Authority_Name.asc()).all()

    if request.method == 'POST':
        cert_name = request.form.get('certificate_name', '').strip()
        issue_date_str = request.form.get('issue_date', '').strip()
        expiry_date_str = request.form.get('expiry_date', '').strip()
        grade = request.form.get('grade', '').strip()
        student_id = request.form.get('student_id', type=int)
        type_id = request.form.get('type_id', type=int)
        authority_id = request.form.get('authority_id', type=int)
        cert_file = request.files.get('certificate_file')

        if not cert_name or not issue_date_str:
            flash('Certificate Name and Issue Date are required.', 'danger')
            return render_template('certificates/form.html', action='Edit', cert=cert, students=students, types=types, authorities=authorities)

        if not student_id or not Student.query.get(student_id):
            flash('Please select a valid Student.', 'danger')
            return render_template('certificates/form.html', action='Edit', cert=cert, students=students, types=types, authorities=authorities)

        if not type_id or not CertificateType.query.get(type_id):
            flash('Please select a valid Certificate Type.', 'danger')
            return render_template('certificates/form.html', action='Edit', cert=cert, students=students, types=types, authorities=authorities)

        if not authority_id or not IssuingAuthority.query.get(authority_id):
            flash('Please select a valid Issuing Authority.', 'danger')
            return render_template('certificates/form.html', action='Edit', cert=cert, students=students, types=types, authorities=authorities)

        try:
            issue_date = datetime.datetime.strptime(issue_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid Issue Date format.', 'danger')
            return render_template('certificates/form.html', action='Edit', cert=cert, students=students, types=types, authorities=authorities)

        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
                if expiry_date < issue_date:
                    flash('Expiry Date must be greater than or equal to Issue Date.', 'danger')
                    return render_template('certificates/form.html', action='Edit', cert=cert, students=students, types=types, authorities=authorities)
            except ValueError:
                flash('Invalid Expiry Date format.', 'danger')
                return render_template('certificates/form.html', action='Edit', cert=cert, students=students, types=types, authorities=authorities)

        # File upload update if provided
        if cert_file and cert_file.filename:
            file_path = save_uploaded_certificate(cert_file)
            if file_path:
                cert.Certificate_File = file_path

        cert.Certificate_Name = cert_name
        cert.Issue_Date = issue_date
        cert.Expiry_Date = expiry_date
        cert.Grade = grade or None
        cert.Student_ID = student_id
        cert.Type_ID = type_id
        cert.Authority_ID = authority_id

        # Auto adjust status if currently active but expired
        today = datetime.date.today()
        if cert.Status == 'Active' and expiry_date and expiry_date < today:
            cert.Status = 'Expired'
        elif cert.Status == 'Expired' and (expiry_date is None or expiry_date >= today):
            cert.Status = 'Active'

        try:
            db.session.commit()
            log_audit(f"Updated certificate: {cert.Certificate_Number}")
            flash(f"Certificate '{cert.Certificate_Number}' updated successfully!", 'success')
            return redirect(url_for('certificates.detail', id=cert.Certificate_ID))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred while updating certificate.", 'danger')

    return render_template('certificates/form.html', action='Edit', cert=cert, students=students, types=types, authorities=authorities)


@certificates_bp.route('/<int:id>/revoke', methods=['POST'])
@login_required
@role_required(['Admin', 'Staff'])
def revoke(id):
    cert = Certificate.query.get_or_404(id)
    reason = request.form.get('reason', '').strip()
    revoked_date_str = request.form.get('revoked_date', '').strip()

    if not reason:
        flash("A revocation reason is required.", "danger")
        return redirect(url_for('certificates.detail', id=id))

    revoked_date = datetime.date.today()
    if revoked_date_str:
        try:
            revoked_date = datetime.datetime.strptime(revoked_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    # Calculate partial key Revocation_No for this certificate
    max_no = db.session.query(db.func.max(Revocation.Revocation_No)).filter_by(Certificate_ID=id).scalar() or 0
    next_revocation_no = max_no + 1

    revocation = Revocation(
        Certificate_ID=id,
        Revocation_No=next_revocation_no,
        Reason=reason,
        Revoked_Date=revoked_date,
        User_ID=current_user.User_ID
    )

    cert.Status = 'Revoked'
    db.session.add(revocation)

    try:
        db.session.commit()
        log_audit(f"Revoked certificate: {cert.Certificate_Number} (Reason: {reason})")

        # Notify student
        notify_student_certificate(
            cert.Student_ID,
            f"Your certificate '{cert.Certificate_Name}' ({cert.Certificate_Number}) has been REVOKED. Reason: {reason}"
        )

        # Notify administrators
        notify_admins(
            f"Certificate '{cert.Certificate_Name}' ({cert.Certificate_Number}) was revoked by {current_user.Username}."
        )

        flash(f"Certificate '{cert.Certificate_Number}' has been revoked.", "warning")
    except IntegrityError as e:
        db.session.rollback()
        flash(f"Failed to record revocation: {e}", "danger")

    return redirect(url_for('certificates.detail', id=id))


@certificates_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required(['Admin'])
def delete(id):
    cert = Certificate.query.get_or_404(id)
    cert_no = cert.Certificate_Number

    try:
        db.session.delete(cert)
        db.session.commit()
        log_audit(f"Deleted certificate: {cert_no}")
        flash(f"Certificate '{cert_no}' and its associated revocations were deleted.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete certificate '{cert_no}': record is referenced by other tables.", "danger")

    return redirect(url_for('certificates.index'))
