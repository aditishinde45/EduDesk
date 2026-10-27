from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import User, Student
from utils.decorators import role_required
from utils.audit import log_audit

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/')
@login_required
@role_required(['Admin'])
def index():
    search = request.args.get('search', '').strip()
    role_filter = request.args.get('role', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = User.query
    if search:
        query = query.filter(
            (User.Username.ilike(f'%{search}%')) |
            (User.Email.ilike(f'%{search}%'))
        )
    if role_filter:
        query = query.filter(User.Role == role_filter)

    pagination = query.order_by(User.User_ID.desc()).paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items

    return render_template('users/index.html', users=users, pagination=pagination, search=search, selected_role=role_filter)


@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def add():
    students = Student.query.order_by(Student.First_Name.asc()).all()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', '').strip()
        email = request.form.get('email', '').strip()
        student_id = request.form.get('student_id', type=int)

        if not username or not password or not role:
            flash('Username, Password, and Role are required.', 'danger')
            return render_template('users/form.html', action='Add', user=None, students=students)

        if role not in ('Admin', 'Staff', 'Student'):
            flash('Role must be Admin, Staff, or Student.', 'danger')
            return render_template('users/form.html', action='Add', user=None, students=students)

        if User.query.filter_by(Username=username).first():
            flash(f"Username '{username}' already exists.", 'danger')
            return render_template('users/form.html', action='Add', user=None, students=students)

        if email and User.query.filter_by(Email=email).first():
            flash(f"Email '{email}' already exists.", 'danger')
            return render_template('users/form.html', action='Add', user=None, students=students)

        new_user = User(
            Username=username,
            Role=role,
            Email=email or None,
            Student_ID=student_id if (role == 'Student' and student_id) else None
        )
        new_user.set_password(password)
        db.session.add(new_user)

        try:
            db.session.commit()
            log_audit(f"Created user '{username}' with role '{role}'")
            flash(f"User '{username}' created successfully!", 'success')
            return redirect(url_for('users.index'))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred. Make sure username and email are unique.", 'danger')

    return render_template('users/form.html', action='Add', user=None, students=students)


@users_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def edit(id):
    user_to_edit = User.query.get_or_404(id)
    students = Student.query.order_by(Student.First_Name.asc()).all()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        role = request.form.get('role', '').strip()
        email = request.form.get('email', '').strip()
        student_id = request.form.get('student_id', type=int)

        if not username or not role:
            flash('Username and Role are required.', 'danger')
            return render_template('users/form.html', action='Edit', user=user_to_edit, students=students)

        if role not in ('Admin', 'Staff', 'Student'):
            flash('Role must be Admin, Staff, or Student.', 'danger')
            return render_template('users/form.html', action='Edit', user=user_to_edit, students=students)

        existing_user = User.query.filter(User.Username == username, User.User_ID != id).first()
        if existing_user:
            flash(f"Username '{username}' is already taken.", 'danger')
            return render_template('users/form.html', action='Edit', user=user_to_edit, students=students)

        if email:
            existing_email = User.query.filter(User.Email == email, User.User_ID != id).first()
            if existing_email:
                flash(f"Email '{email}' is already taken.", 'danger')
                return render_template('users/form.html', action='Edit', user=user_to_edit, students=students)

        user_to_edit.Username = username
        user_to_edit.Role = role
        user_to_edit.Email = email or None
        user_to_edit.Student_ID = student_id if (role == 'Student' and student_id) else None

        try:
            db.session.commit()
            log_audit(f"Updated user details for '{user_to_edit.Username}'")
            flash(f"User '{user_to_edit.Username}' updated successfully!", 'success')
            return redirect(url_for('users.index'))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred while updating user.", 'danger')

    return render_template('users/form.html', action='Edit', user=user_to_edit, students=students)


@users_bp.route('/<int:id>/reset-password', methods=['POST'])
@login_required
@role_required(['Admin'])
def reset_password(id):
    target_user = User.query.get_or_404(id)
    new_password = request.form.get('new_password', '').strip()

    if not new_password or len(new_password) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect(url_for('users.index'))

    target_user.set_password(new_password)
    db.session.commit()
    log_audit(f"Password reset for user '{target_user.Username}' by admin")
    flash(f"Password for user '{target_user.Username}' has been reset successfully.", "success")
    return redirect(url_for('users.index'))


@users_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required(['Admin'])
def delete(id):
    target_user = User.query.get_or_404(id)
    uname = target_user.Username

    if target_user.User_ID == current_user.User_ID:
        flash("You cannot delete your own active administrator account.", "danger")
        return redirect(url_for('users.index'))

    try:
        db.session.delete(target_user)
        db.session.commit()
        log_audit(f"Deleted user: {uname}")
        flash(f"User '{uname}' deleted successfully.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete user '{uname}': this user has associated audit logs or revocations.", "danger")

    return redirect(url_for('users.index'))
