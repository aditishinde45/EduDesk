from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Department
from utils.decorators import role_required
from utils.audit import log_audit

departments_bp = Blueprint('departments', __name__, url_prefix='/departments')

@departments_bp.route('/')
@login_required
@role_required(['Admin', 'Staff'])
def index():
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Department.query
    if search:
        query = query.filter(
            (Department.Department_Name.ilike(f'%{search}%')) |
            (Department.HOD_Name.ilike(f'%{search}%')) |
            (Department.Email.ilike(f'%{search}%'))
        )

    pagination = query.order_by(Department.Department_Name.asc()).paginate(page=page, per_page=per_page, error_out=False)
    departments = pagination.items

    return render_template('departments/index.html', departments=departments, pagination=pagination, search=search)


@departments_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def add():
    if request.method == 'POST':
        name = request.form.get('department_name', '').strip()
        hod = request.form.get('hod_name', '').strip()
        email = request.form.get('email', '').strip()

        if not name:
            flash('Department Name is required.', 'danger')
            return render_template('departments/form.html', action='Add', department=None)

        # Check unique constraints
        if Department.query.filter_by(Department_Name=name).first():
            flash(f"Department with name '{name}' already exists.", 'danger')
            return render_template('departments/form.html', action='Add', department=None)

        if email and Department.query.filter_by(Email=email).first():
            flash(f"Department with email '{email}' already exists.", 'danger')
            return render_template('departments/form.html', action='Add', department=None)

        dept = Department(
            Department_Name=name,
            HOD_Name=hod or None,
            Email=email or None
        )
        db.session.add(dept)
        try:
            db.session.commit()
            log_audit(f"Created department: {dept.Department_Name}")
            flash(f"Department '{dept.Department_Name}' created successfully!", 'success')
            return redirect(url_for('departments.index'))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred. Make sure department name and email are unique.", "danger")

    return render_template('departments/form.html', action='Add', department=None)


@departments_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def edit(id):
    dept = Department.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form.get('department_name', '').strip()
        hod = request.form.get('hod_name', '').strip()
        email = request.form.get('email', '').strip()

        if not name:
            flash('Department Name is required.', 'danger')
            return render_template('departments/form.html', action='Edit', department=dept)

        # Check unique constraints against other records
        existing_name = Department.query.filter(Department.Department_Name == name, Department.Department_ID != id).first()
        if existing_name:
            flash(f"Department with name '{name}' already exists.", 'danger')
            return render_template('departments/form.html', action='Edit', department=dept)

        if email:
            existing_email = Department.query.filter(Department.Email == email, Department.Department_ID != id).first()
            if existing_email:
                flash(f"Department with email '{email}' already exists.", 'danger')
                return render_template('departments/form.html', action='Edit', department=dept)

        dept.Department_Name = name
        dept.HOD_Name = hod or None
        dept.Email = email or None

        try:
            db.session.commit()
            log_audit(f"Updated department: {dept.Department_Name}")
            flash(f"Department '{dept.Department_Name}' updated successfully!", 'success')
            return redirect(url_for('departments.index'))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred while updating the department.", "danger")

    return render_template('departments/form.html', action='Edit', department=dept)


@departments_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required(['Admin'])
def delete(id):
    dept = Department.query.get_or_404(id)
    dept_name = dept.Department_Name

    # Check for foreign key references before delete to prevent crashing on RESTRICT
    if dept.courses and len(dept.courses) > 0:
        flash(f"Cannot delete department '{dept_name}': it still has {len(dept.courses)} courses associated with it.", "danger")
        return redirect(url_for('departments.index'))

    if dept.students and len(dept.students) > 0:
        flash(f"Cannot delete department '{dept_name}': it still has {len(dept.students)} students enrolled.", "danger")
        return redirect(url_for('departments.index'))

    try:
        db.session.delete(dept)
        db.session.commit()
        log_audit(f"Deleted department: {dept_name}")
        flash(f"Department '{dept_name}' deleted successfully.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete department '{dept_name}': it is referenced by other database records.", "danger")

    return redirect(url_for('departments.index'))
