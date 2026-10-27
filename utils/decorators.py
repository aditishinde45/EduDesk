from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user
from models import Student

def role_required(allowed_roles):
    """
    Decorator to enforce Role-Based Access Control on Flask view functions.
    allowed_roles: list of roles e.g. ['Admin', 'Staff']
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for('auth.login'))

            if current_user.Role not in allowed_roles:
                # Return 403 Forbidden with user-friendly error page
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_current_student():
    """
    Finds the Student record corresponding to the current logged-in user.
    Uses either the direct Student_ID foreign key on Users, or matches by Email.
    """
    if not current_user.is_authenticated or current_user.Role != 'Student':
        return None

    if current_user.Student_ID:
        student = Student.query.get(current_user.Student_ID)
        if student:
            return student

    if current_user.Email:
        student = Student.query.filter_by(Email=current_user.Email).first()
        if student:
            return student

    return None
