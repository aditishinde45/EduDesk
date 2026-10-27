from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Department, Course, Student, Certificate, AuditLog, Notification
from utils.decorators import get_current_student
from utils.expiry import check_and_update_expired_certificates

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Run auto-expiry check on dashboard load
    check_and_update_expired_certificates()

    # Determine user role and load appropriate data
    if current_user.is_student:
        student = get_current_student()
        student_id = student.Student_ID if student else None

        if student_id:
            active_certs = Certificate.query.filter_by(Student_ID=student_id, Status='Active').count()
            expired_certs = Certificate.query.filter_by(Student_ID=student_id, Status='Expired').count()
            revoked_certs = Certificate.query.filter_by(Student_ID=student_id, Status='Revoked').count()
            total_certs = Certificate.query.filter_by(Student_ID=student_id).count()
            recent_certs = Certificate.query.filter_by(Student_ID=student_id).order_by(Certificate.Issue_Date.desc()).limit(5).all()
        else:
            active_certs = expired_certs = revoked_certs = total_certs = 0
            recent_certs = []

        recent_notifications = Notification.query.filter_by(User_ID=current_user.User_ID).order_by(Notification.Sent_Date.desc()).limit(5).all()

        return render_template(
            'dashboard/student_dashboard.html',
            student=student,
            active_certs=active_certs,
            expired_certs=expired_certs,
            revoked_certs=revoked_certs,
            total_certs=total_certs,
            recent_certs=recent_certs,
            recent_notifications=recent_notifications
        )

    # Admin / Staff Dashboard
    student_count = Student.query.count()
    course_count = Course.query.count()
    dept_count = Department.query.count()

    active_certs = Certificate.query.filter_by(Status='Active').count()
    expired_certs = Certificate.query.filter_by(Status='Expired').count()
    revoked_certs = Certificate.query.filter_by(Status='Revoked').count()
    total_certs = Certificate.query.count()

    recent_certs = Certificate.query.order_by(Certificate.Certificate_ID.desc()).limit(5).all()

    recent_logs = []
    if current_user.is_admin:
        recent_logs = AuditLog.query.order_by(AuditLog.Timestamp.desc()).limit(7).all()

    recent_notifications = Notification.query.filter_by(User_ID=current_user.User_ID).order_by(Notification.Sent_Date.desc()).limit(5).all()

    return render_template(
        'dashboard/index.html',
        student_count=student_count,
        course_count=course_count,
        dept_count=dept_count,
        active_certs=active_certs,
        expired_certs=expired_certs,
        revoked_certs=revoked_certs,
        total_certs=total_certs,
        recent_certs=recent_certs,
        recent_logs=recent_logs,
        recent_notifications=recent_notifications
    )
