import io
import csv
import datetime
from flask import Blueprint, render_template, request, Response
from flask_login import login_required
from sqlalchemy import func
from extensions import db
from models import Certificate, Student, Department, Course, CertificateType, IssuingAuthority
from utils.decorators import role_required
from utils.expiry import check_and_update_expired_certificates

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/issued')
@login_required
@role_required(['Admin', 'Staff'])
def issued():
    check_and_update_expired_certificates()

    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()
    dept_id = request.args.get('department_id', type=int)
    type_id = request.args.get('type_id', type=int)

    query = Certificate.query.join(Student).join(Department).join(CertificateType).join(IssuingAuthority)

    if date_from_str:
        try:
            d_from = datetime.datetime.strptime(date_from_str, '%Y-%m-%d').date()
            query = query.filter(Certificate.Issue_Date >= d_from)
        except ValueError:
            pass

    if date_to_str:
        try:
            d_to = datetime.datetime.strptime(date_to_str, '%Y-%m-%d').date()
            query = query.filter(Certificate.Issue_Date <= d_to)
        except ValueError:
            pass

    if dept_id:
        query = query.filter(Student.Department_ID == dept_id)

    if type_id:
        query = query.filter(Certificate.Type_ID == type_id)

    certificates = query.order_by(Certificate.Issue_Date.desc()).all()
    departments = Department.query.order_by(Department.Department_Name.asc()).all()
    cert_types = CertificateType.query.order_by(CertificateType.Type_Name.asc()).all()

    return render_template(
        'reports/issued.html',
        certificates=certificates,
        departments=departments,
        cert_types=cert_types,
        date_from=date_from_str,
        date_to=date_to_str,
        selected_dept_id=dept_id,
        selected_type_id=type_id
    )


@reports_bp.route('/issued/export')
@login_required
@role_required(['Admin', 'Staff'])
def export_issued():
    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()
    dept_id = request.args.get('department_id', type=int)
    type_id = request.args.get('type_id', type=int)

    query = Certificate.query.join(Student).join(Department).join(Course).join(CertificateType).join(IssuingAuthority)

    if date_from_str:
        try:
            d_from = datetime.datetime.strptime(date_from_str, '%Y-%m-%d').date()
            query = query.filter(Certificate.Issue_Date >= d_from)
        except ValueError:
            pass

    if date_to_str:
        try:
            d_to = datetime.datetime.strptime(date_to_str, '%Y-%m-%d').date()
            query = query.filter(Certificate.Issue_Date <= d_to)
        except ValueError:
            pass

    if dept_id:
        query = query.filter(Student.Department_ID == dept_id)

    if type_id:
        query = query.filter(Certificate.Type_ID == type_id)

    certificates = query.order_by(Certificate.Issue_Date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Certificate Number', 'Certificate Name', 'Student Name', 'Enrollment No',
        'Department', 'Course', 'Certificate Type', 'Issuing Authority',
        'Issue Date', 'Expiry Date', 'Grade', 'Status'
    ])

    for c in certificates:
        writer.writerow([
            c.Certificate_Number,
            c.Certificate_Name,
            c.student.full_name,
            c.student.Enrollment_No,
            c.student.department.Department_Name,
            c.student.course.Course_Name,
            c.certificate_type.Type_Name,
            c.authority.Authority_Name,
            c.Issue_Date,
            c.Expiry_Date or 'N/A',
            c.Grade or 'N/A',
            c.Status
        ])

    filename = f"Issued_Certificates_{datetime.date.today()}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@reports_bp.route('/expired')
@login_required
@role_required(['Admin', 'Staff'])
def expired():
    check_and_update_expired_certificates()

    query = Certificate.query.join(Student).join(Department).join(CertificateType).filter(
        Certificate.Status == 'Expired'
    )
    certificates = query.order_by(Certificate.Expiry_Date.desc()).all()

    return render_template('reports/expired.html', certificates=certificates)


@reports_bp.route('/expired/export')
@login_required
@role_required(['Admin', 'Staff'])
def export_expired():
    query = Certificate.query.join(Student).join(Department).join(Course).join(CertificateType).join(IssuingAuthority).filter(
        Certificate.Status == 'Expired'
    )
    certificates = query.order_by(Certificate.Expiry_Date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Certificate Number', 'Certificate Name', 'Student Name', 'Enrollment No',
        'Department', 'Course', 'Certificate Type', 'Issuing Authority',
        'Issue Date', 'Expiry Date', 'Grade'
    ])

    for c in certificates:
        writer.writerow([
            c.Certificate_Number,
            c.Certificate_Name,
            c.student.full_name,
            c.student.Enrollment_No,
            c.student.department.Department_Name,
            c.student.course.Course_Name,
            c.certificate_type.Type_Name,
            c.authority.Authority_Name,
            c.Issue_Date,
            c.Expiry_Date,
            c.Grade or 'N/A'
        ])

    filename = f"Expired_Certificates_{datetime.date.today()}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@reports_bp.route('/summary')
@login_required
@role_required(['Admin', 'Staff'])
def summary():
    check_and_update_expired_certificates()

    # Counts by Certificate Type
    type_stats = db.session.query(
        CertificateType.Type_Name,
        func.count(Certificate.Certificate_ID).label('total'),
        func.sum(db.case((Certificate.Status == 'Active', 1), else_=0)).label('active'),
        func.sum(db.case((Certificate.Status == 'Expired', 1), else_=0)).label('expired'),
        func.sum(db.case((Certificate.Status == 'Revoked', 1), else_=0)).label('revoked')
    ).outerjoin(Certificate, CertificateType.Type_ID == Certificate.Type_ID)\
     .group_by(CertificateType.Type_Name)\
     .order_by(CertificateType.Type_Name.asc()).all()

    # Counts by Department
    dept_stats = db.session.query(
        Department.Department_Name,
        func.count(Certificate.Certificate_ID).label('total'),
        func.sum(db.case((Certificate.Status == 'Active', 1), else_=0)).label('active'),
        func.sum(db.case((Certificate.Status == 'Expired', 1), else_=0)).label('expired'),
        func.sum(db.case((Certificate.Status == 'Revoked', 1), else_=0)).label('revoked')
    ).outerjoin(Student, Department.Department_ID == Student.Department_ID)\
     .outerjoin(Certificate, Student.Student_ID == Certificate.Student_ID)\
     .group_by(Department.Department_Name)\
     .order_by(Department.Department_Name.asc()).all()

    # Overall Status distribution
    active_total = Certificate.query.filter_by(Status='Active').count()
    expired_total = Certificate.query.filter_by(Status='Expired').count()
    revoked_total = Certificate.query.filter_by(Status='Revoked').count()
    grand_total = Certificate.query.count()

    return render_template(
        'reports/summary.html',
        type_stats=type_stats,
        dept_stats=dept_stats,
        active_total=active_total,
        expired_total=expired_total,
        revoked_total=revoked_total,
        grand_total=grand_total
    )


@reports_bp.route('/summary/export')
@login_required
@role_required(['Admin', 'Staff'])
def export_summary():
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['CERTIFICATION SUMMARY REPORT'])
    writer.writerow(['Generated on', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])

    writer.writerow(['--- SUMMARY BY CERTIFICATE TYPE ---'])
    writer.writerow(['Certificate Type', 'Active', 'Expired', 'Revoked', 'Total'])

    type_stats = db.session.query(
        CertificateType.Type_Name,
        func.count(Certificate.Certificate_ID).label('total'),
        func.sum(db.case((Certificate.Status == 'Active', 1), else_=0)).label('active'),
        func.sum(db.case((Certificate.Status == 'Expired', 1), else_=0)).label('expired'),
        func.sum(db.case((Certificate.Status == 'Revoked', 1), else_=0)).label('revoked')
    ).outerjoin(Certificate, CertificateType.Type_ID == Certificate.Type_ID)\
     .group_by(CertificateType.Type_Name)\
     .order_by(CertificateType.Type_Name.asc()).all()

    for row in type_stats:
        writer.writerow([row[0], int(row[2] or 0), int(row[3] or 0), int(row[4] or 0), int(row[1] or 0)])

    writer.writerow([])
    writer.writerow(['--- SUMMARY BY DEPARTMENT ---'])
    writer.writerow(['Department Name', 'Active', 'Expired', 'Revoked', 'Total'])

    dept_stats = db.session.query(
        Department.Department_Name,
        func.count(Certificate.Certificate_ID).label('total'),
        func.sum(db.case((Certificate.Status == 'Active', 1), else_=0)).label('active'),
        func.sum(db.case((Certificate.Status == 'Expired', 1), else_=0)).label('expired'),
        func.sum(db.case((Certificate.Status == 'Revoked', 1), else_=0)).label('revoked')
    ).outerjoin(Student, Department.Department_ID == Student.Department_ID)\
     .outerjoin(Certificate, Student.Student_ID == Certificate.Student_ID)\
     .group_by(Department.Department_Name)\
     .order_by(Department.Department_Name.asc()).all()

    for row in dept_stats:
        writer.writerow([row[0], int(row[2] or 0), int(row[3] or 0), int(row[4] or 0), int(row[1] or 0)])

    filename = f"Certificate_Summary_Report_{datetime.date.today()}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
