from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Course, Department
from utils.decorators import role_required
from utils.audit import log_audit

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

@courses_bp.route('/')
@login_required
@role_required(['Admin', 'Staff'])
def index():
    search = request.args.get('search', '').strip()
    dept_id = request.args.get('department_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Course.query.join(Department)
    if search:
        query = query.filter(
            (Course.Course_Name.ilike(f'%{search}%')) |
            (Department.Department_Name.ilike(f'%{search}%'))
        )
    if dept_id:
        query = query.filter(Course.Department_ID == dept_id)

    pagination = query.order_by(Course.Course_Name.asc()).paginate(page=page, per_page=per_page, error_out=False)
    courses = pagination.items
    departments = Department.query.order_by(Department.Department_Name.asc()).all()

    return render_template(
        'courses/index.html',
        courses=courses,
        pagination=pagination,
        search=search,
        selected_dept_id=dept_id,
        departments=departments
    )


@courses_bp.route('/by-department/<int:dept_id>')
@login_required
def by_department(dept_id):
    """JSON API to fetch courses belonging to a specific department (used for dynamic dropdowns)."""
    courses = Course.query.filter_by(Department_ID=dept_id).order_by(Course.Course_Name.asc()).all()
    return jsonify([
        {'id': c.Course_ID, 'name': c.Course_Name, 'duration': c.Duration}
        for c in courses
    ])


@courses_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def add():
    departments = Department.query.order_by(Department.Department_Name.asc()).all()

    if request.method == 'POST':
        name = request.form.get('course_name', '').strip()
        duration = request.form.get('duration', '').strip()
        dept_id = request.form.get('department_id', type=int)

        if not name:
            flash('Course Name is required.', 'danger')
            return render_template('courses/form.html', action='Add', course=None, departments=departments)

        if not dept_id or not Department.query.get(dept_id):
            flash('Please select a valid Department.', 'danger')
            return render_template('courses/form.html', action='Add', course=None, departments=departments)

        course = Course(
            Course_Name=name,
            Duration=duration or None,
            Department_ID=dept_id
        )
        db.session.add(course)
        try:
            db.session.commit()
            log_audit(f"Created course: {course.Course_Name}")
            flash(f"Course '{course.Course_Name}' created successfully!", 'success')
            return redirect(url_for('courses.index'))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred while creating the course.", 'danger')

    return render_template('courses/form.html', action='Add', course=None, departments=departments)


@courses_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def edit(id):
    course = Course.query.get_or_404(id)
    departments = Department.query.order_by(Department.Department_Name.asc()).all()

    if request.method == 'POST':
        name = request.form.get('course_name', '').strip()
        duration = request.form.get('duration', '').strip()
        dept_id = request.form.get('department_id', type=int)

        if not name:
            flash('Course Name is required.', 'danger')
            return render_template('courses/form.html', action='Edit', course=course, departments=departments)

        if not dept_id or not Department.query.get(dept_id):
            flash('Please select a valid Department.', 'danger')
            return render_template('courses/form.html', action='Edit', course=course, departments=departments)

        course.Course_Name = name
        course.Duration = duration or None
        course.Department_ID = dept_id

        try:
            db.session.commit()
            log_audit(f"Updated course: {course.Course_Name}")
            flash(f"Course '{course.Course_Name}' updated successfully!", 'success')
            return redirect(url_for('courses.index'))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred while updating the course.", 'danger')

    return render_template('courses/form.html', action='Edit', course=course, departments=departments)


@courses_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required(['Admin'])
def delete(id):
    course = Course.query.get_or_404(id)
    course_name = course.Course_Name

    if course.students and len(course.students) > 0:
        flash(f"Cannot delete course '{course_name}': it still has {len(course.students)} students enrolled.", "danger")
        return redirect(url_for('courses.index'))

    try:
        db.session.delete(course)
        db.session.commit()
        log_audit(f"Deleted course: {course_name}")
        flash(f"Course '{course_name}' deleted successfully.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete course '{course_name}': it is referenced by other records.", "danger")

    return redirect(url_for('courses.index'))
