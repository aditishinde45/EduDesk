from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from models import Revocation, Certificate, Student
from utils.decorators import get_current_student

revocations_bp = Blueprint('revocations', __name__, url_prefix='/revocations')

@revocations_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Revocation.query.join(Certificate).join(Student)

    # Student isolation
    if current_user.is_student:
        student = get_current_student()
        if not student:
            return render_template('revocations/index.html', revocations=[], pagination=None, search='')
        query = query.filter(Certificate.Student_ID == student.Student_ID)

    if search:
        query = query.filter(
            (Certificate.Certificate_Number.ilike(f'%{search}%')) |
            (Certificate.Certificate_Name.ilike(f'%{search}%')) |
            (Student.First_Name.ilike(f'%{search}%')) |
            (Student.Enrollment_No.ilike(f'%{search}%')) |
            (Revocation.Reason.ilike(f'%{search}%'))
        )

    pagination = query.order_by(Revocation.Revoked_Date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    revocations = pagination.items

    return render_template('revocations/index.html', revocations=revocations, pagination=pagination, search=search)
