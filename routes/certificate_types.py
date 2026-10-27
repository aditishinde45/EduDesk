from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import CertificateType
from utils.decorators import role_required
from utils.audit import log_audit

certificate_types_bp = Blueprint('certificate_types', __name__, url_prefix='/certificate-types')

@certificate_types_bp.route('/')
@login_required
@role_required(['Admin', 'Staff'])
def index():
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = CertificateType.query
    if search:
        query = query.filter(
            (CertificateType.Type_Name.ilike(f'%{search}%')) |
            (CertificateType.Description.ilike(f'%{search}%'))
        )

    pagination = query.order_by(CertificateType.Type_Name.asc()).paginate(page=page, per_page=per_page, error_out=False)
    types = pagination.items

    return render_template('certificate_types/index.html', types=types, pagination=pagination, search=search)


@certificate_types_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def add():
    if request.method == 'POST':
        name = request.form.get('type_name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Type Name is required.', 'danger')
            return render_template('certificate_types/form.html', action='Add', cert_type=None)

        if CertificateType.query.filter_by(Type_Name=name).first():
            flash(f"Certificate Type '{name}' already exists.", 'danger')
            return render_template('certificate_types/form.html', action='Add', cert_type=None)

        cert_type = CertificateType(
            Type_Name=name,
            Description=description or None
        )
        db.session.add(cert_type)
        try:
            db.session.commit()
            log_audit(f"Created certificate type: {cert_type.Type_Name}")
            flash(f"Certificate Type '{cert_type.Type_Name}' created successfully!", 'success')
            return redirect(url_for('certificate_types.index'))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred. Certificate Type name must be unique.", 'danger')

    return render_template('certificate_types/form.html', action='Add', cert_type=None)


@certificate_types_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def edit(id):
    cert_type = CertificateType.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form.get('type_name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Type Name is required.', 'danger')
            return render_template('certificate_types/form.html', action='Edit', cert_type=cert_type)

        existing = CertificateType.query.filter(
            CertificateType.Type_Name == name,
            CertificateType.Type_ID != id
        ).first()
        if existing:
            flash(f"Certificate Type '{name}' already exists.", 'danger')
            return render_template('certificate_types/form.html', action='Edit', cert_type=cert_type)

        cert_type.Type_Name = name
        cert_type.Description = description or None

        try:
            db.session.commit()
            log_audit(f"Updated certificate type: {cert_type.Type_Name}")
            flash(f"Certificate Type '{cert_type.Type_Name}' updated successfully!", 'success')
            return redirect(url_for('certificate_types.index'))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred while updating the certificate type.", 'danger')

    return render_template('certificate_types/form.html', action='Edit', cert_type=cert_type)


@certificate_types_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required(['Admin', 'Staff'])
def delete(id):
    cert_type = CertificateType.query.get_or_404(id)
    type_name = cert_type.Type_Name

    if cert_type.certificates and len(cert_type.certificates) > 0:
        flash(f"Cannot delete certificate type '{type_name}': it is associated with {len(cert_type.certificates)} existing certificates.", 'danger')
        return redirect(url_for('certificate_types.index'))

    try:
        db.session.delete(cert_type)
        db.session.commit()
        log_audit(f"Deleted certificate type: {type_name}")
        flash(f"Certificate Type '{type_name}' deleted successfully.", 'success')
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete certificate type '{type_name}': it is referenced by existing certificates.", 'danger')

    return redirect(url_for('certificate_types.index'))
