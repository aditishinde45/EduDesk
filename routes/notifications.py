from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Notification

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 15

    # Admins can optionally view all notifications or their own; Staff/Student view their own
    view_all = request.args.get('all', '0') == '1' and current_user.is_admin

    if view_all:
        query = Notification.query
    else:
        query = Notification.query.filter_by(User_ID=current_user.User_ID)

    pagination = query.order_by(Notification.Sent_Date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    notifications = pagination.items

    return render_template(
        'notifications/index.html',
        notifications=notifications,
        pagination=pagination,
        view_all=view_all
    )


@notifications_bp.route('/<int:id>/mark-read', methods=['POST'])
@login_required
def mark_read(id):
    notif = Notification.query.get_or_404(id)

    # Security check: users can only mark their own notifications as read unless admin
    if notif.User_ID != current_user.User_ID and not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Forbidden'}), 403

    notif.Status = 'Read'
    db.session.commit()

    if request.is_json:
        return jsonify({'success': True})

    flash("Notification marked as read.", "success")
    return redirect(url_for('notifications.index'))


@notifications_bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(User_ID=current_user.User_ID, Status='Unread').update({'Status': 'Read'})
    db.session.commit()
    flash("All notifications marked as read.", "success")
    return redirect(url_for('notifications.index'))


@notifications_bp.route('/api/unread-count')
@login_required
def unread_count():
    count = Notification.query.filter_by(User_ID=current_user.User_ID, Status='Unread').count()
    return jsonify({'unread_count': count})
