import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
from utils.audit import log_audit

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('auth/login.html', username=username)

        user = User.query.filter_by(Username=username).first()

        if user and user.check_password(password):
            login_user(user)
            user.Last_Login = datetime.datetime.utcnow()
            db.session.commit()

            # Record audit log
            log_audit(f"Login successful for user '{user.Username}'", user_id=user.User_ID)

            flash(f"Welcome back, {user.Username}!", "success")

            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.Username
    user_id = current_user.User_ID
    logout_user()
    log_audit(f"User logged out: {username}", user_id=user_id)
    flash("You have been successfully logged out.", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not current_user.check_password(old_password):
            flash("Current password is incorrect.", "danger")
            return render_template('auth/change_password.html')

        if len(new_password) < 6:
            flash("New password must be at least 6 characters long.", "danger")
            return render_template('auth/change_password.html')

        if new_password != confirm_password:
            flash("New password and confirm password do not match.", "danger")
            return render_template('auth/change_password.html')

        current_user.set_password(new_password)
        db.session.commit()
        log_audit(f"Password changed for user '{current_user.Username}'", user_id=current_user.User_ID)
        flash("Password updated successfully!", "success")
        return redirect(url_for('dashboard.index'))

    return render_template('auth/change_password.html')
