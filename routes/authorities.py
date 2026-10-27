import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import IssuingAuthority, AuthorityPhone
from utils.decorators import role_required
from utils.audit import log_audit

authorities_bp = Blueprint('authorities', __name__, url_prefix='/authorities')

PHONE_REGEX = re.compile(r'^\+?[0-9]{10,15}$')
PINCODE_REGEX = re.compile(r'^[0-9]{6}$')

@authorities_bp.route('/')
@login_required
@role_required(['Admin', 'Staff'])
def index():
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = IssuingAuthority.query
    if search:
        query = query.filter(
            (IssuingAuthority.Authority_Name.ilike(f'%{search}%')) |
            (IssuingAuthority.Registration_No.ilike(f'%{search}%')) |
            (IssuingAuthority.City.ilike(f'%{search}%')) |
            (IssuingAuthority.Email.ilike(f'%{search}%'))
        )

    pagination = query.order_by(IssuingAuthority.Authority_Name.asc()).paginate(page=page, per_page=per_page, error_out=False)
    authorities = pagination.items

    return render_template('authorities/index.html', authorities=authorities, pagination=pagination, search=search)


@authorities_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def add():
    if request.method == 'POST':
        name = request.form.get('authority_name', '').strip()
        reg_no = request.form.get('registration_no', '').strip()
        email = request.form.get('email', '').strip()
        website = request.form.get('website', '').strip()
        house_no = request.form.get('house_no', '').strip()
        street = request.form.get('street', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        phones = request.form.getlist('phones[]')

        if not name:
            flash('Authority Name is required.', 'danger')
            return render_template('authorities/form.html', action='Add', authority=None, phones=phones)

        if pincode and not PINCODE_REGEX.match(pincode):
            flash('Pincode must be exactly 6 digits.', 'danger')
            return render_template('authorities/form.html', action='Add', authority=None, phones=phones)

        if reg_no and IssuingAuthority.query.filter_by(Registration_No=reg_no).first():
            flash(f"Registration number '{reg_no}' already exists.", 'danger')
            return render_template('authorities/form.html', action='Add', authority=None, phones=phones)

        # Validate phones
        valid_phones = []
        for p in phones:
            p_clean = p.strip()
            if p_clean:
                if not PHONE_REGEX.match(p_clean):
                    flash(f"Invalid phone number '{p_clean}'. Must be 10 to 15 digits.", 'danger')
                    return render_template('authorities/form.html', action='Add', authority=None, phones=phones)
                if p_clean not in valid_phones:
                    valid_phones.append(p_clean)

        authority = IssuingAuthority(
            Authority_Name=name,
            Registration_No=reg_no or None,
            Email=email or None,
            Website=website or None,
            House_no=house_no or None,
            Street=street or None,
            City=city or None,
            State=state or None,
            Pincode=pincode or None
        )
        db.session.add(authority)
        db.session.flush()  # to obtain authority.Authority_ID

        # Add phone numbers
        for p in valid_phones:
            db.session.add(AuthorityPhone(Authority_ID=authority.Authority_ID, Phone_No=p))

        try:
            db.session.commit()
            log_audit(f"Created issuing authority: {authority.Authority_Name}")
            flash(f"Issuing Authority '{authority.Authority_Name}' added successfully!", 'success')
            return redirect(url_for('authorities.index'))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred. Check that registration number is unique.", 'danger')

    return render_template('authorities/form.html', action='Add', authority=None, phones=[])


@authorities_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def edit(id):
    authority = IssuingAuthority.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form.get('authority_name', '').strip()
        reg_no = request.form.get('registration_no', '').strip()
        email = request.form.get('email', '').strip()
        website = request.form.get('website', '').strip()
        house_no = request.form.get('house_no', '').strip()
        street = request.form.get('street', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        phones = request.form.getlist('phones[]')

        if not name:
            flash('Authority Name is required.', 'danger')
            return render_template('authorities/form.html', action='Edit', authority=authority, phones=phones)

        if pincode and not PINCODE_REGEX.match(pincode):
            flash('Pincode must be exactly 6 digits.', 'danger')
            return render_template('authorities/form.html', action='Edit', authority=authority, phones=phones)

        if reg_no:
            existing_reg = IssuingAuthority.query.filter(
                IssuingAuthority.Registration_No == reg_no,
                IssuingAuthority.Authority_ID != id
            ).first()
            if existing_reg:
                flash(f"Registration number '{reg_no}' is already used by another authority.", 'danger')
                return render_template('authorities/form.html', action='Edit', authority=authority, phones=phones)

        valid_phones = []
        for p in phones:
            p_clean = p.strip()
            if p_clean:
                if not PHONE_REGEX.match(p_clean):
                    flash(f"Invalid phone number '{p_clean}'. Must be 10 to 15 digits.", 'danger')
                    return render_template('authorities/form.html', action='Edit', authority=authority, phones=phones)
                if p_clean not in valid_phones:
                    valid_phones.append(p_clean)

        authority.Authority_Name = name
        authority.Registration_No = reg_no or None
        authority.Email = email or None
        authority.Website = website or None
        authority.House_no = house_no or None
        authority.Street = street or None
        authority.City = city or None
        authority.State = state or None
        authority.Pincode = pincode or None

        # Update phones: delete old, insert new
        AuthorityPhone.query.filter_by(Authority_ID=id).delete()
        for p in valid_phones:
            db.session.add(AuthorityPhone(Authority_ID=id, Phone_No=p))

        try:
            db.session.commit()
            log_audit(f"Updated issuing authority: {authority.Authority_Name}")
            flash(f"Issuing Authority '{authority.Authority_Name}' updated successfully!", 'success')
            return redirect(url_for('authorities.index'))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred while updating the authority.", 'danger')

    current_phones = [p.Phone_No for p in authority.phones]
    return render_template('authorities/form.html', action='Edit', authority=authority, phones=current_phones)


@authorities_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required(['Admin', 'Staff'])
def delete(id):
    authority = IssuingAuthority.query.get_or_404(id)
    auth_name = authority.Authority_Name

    if authority.certificates and len(authority.certificates) > 0:
        flash(f"Cannot delete authority '{auth_name}': it has {len(authority.certificates)} issued certificates associated with it.", 'danger')
        return redirect(url_for('authorities.index'))

    try:
        db.session.delete(authority)
        db.session.commit()
        log_audit(f"Deleted issuing authority: {auth_name}")
        flash(f"Issuing Authority '{auth_name}' deleted successfully.", 'success')
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete authority '{auth_name}': it is referenced by existing certificates.", 'danger')

    return redirect(url_for('authorities.index'))
