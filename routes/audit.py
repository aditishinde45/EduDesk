import datetime
from flask import Blueprint, render_template, request
from flask_login import login_required
from models import AuditLog, User
from utils.decorators import role_required

audit_bp = Blueprint('audit', __name__, url_prefix='/audit-logs')

@audit_bp.route('/')
@login_required
@role_required(['Admin'])
def index():
    search = request.args.get('search', '').strip()
    user_id = request.args.get('user_id', type=int)
    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 15

    query = AuditLog.query.join(User)

    if search:
        query = query.filter(
            (AuditLog.Action.ilike(f'%{search}%')) |
            (AuditLog.IP_Address.ilike(f'%{search}%')) |
            (User.Username.ilike(f'%{search}%'))
        )

    if user_id:
        query = query.filter(AuditLog.User_ID == user_id)

    if date_from_str:
        try:
            d_from = datetime.datetime.strptime(date_from_str, '%Y-%m-%d')
            query = query.filter(AuditLog.Timestamp >= d_from)
        except ValueError:
            pass

    if date_to_str:
        try:
            d_to = datetime.datetime.strptime(date_to_str, '%Y-%m-%d') + datetime.timedelta(days=1)
            query = query.filter(AuditLog.Timestamp < d_to)
        except ValueError:
            pass

    pagination = query.order_by(AuditLog.Timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    logs = pagination.items
    users = User.query.order_by(User.Username.asc()).all()

    return render_template(
        'audit/index.html',
        logs=logs,
        pagination=pagination,
        search=search,
        selected_user_id=user_id,
        date_from=date_from_str,
        date_to=date_to_str,
        users=users
    )
