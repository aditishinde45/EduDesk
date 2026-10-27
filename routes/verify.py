import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from extensions import db
from models import Certificate, User, AuditLog
from utils.helpers import get_client_ip
from utils.expiry import check_and_update_expired_certificates

verify_bp = Blueprint('verify', __name__)

@verify_bp.route('/verify', methods=['GET', 'POST'])
def search():
    """Public certificate verification search page."""
    if request.method == 'POST':
        cert_no = request.form.get('certificate_number', '').strip()
        if not cert_no:
            flash("Please enter a Certificate Number.", "warning")
            return render_template('verify/verify.html')
        return redirect(url_for('verify.verify_certificate', certificate_number=cert_no))

    return render_template('verify/verify.html')


@verify_bp.route('/verify/<certificate_number>')
def verify_certificate(certificate_number):
    """
    Public verification page for a specific certificate number.
    Accessible without logging in.
    """
    check_and_update_expired_certificates()

    cert = Certificate.query.filter_by(Certificate_Number=certificate_number).first()

    # Log public verification action
    try:
        user_id = current_user.User_ID if (current_user and current_user.is_authenticated) else 1
        log = AuditLog(
            Action=f"Public Verification Query: {certificate_number} (Result: {'Found' if cert else 'Not Found'})",
            Timestamp=datetime.datetime.utcnow(),
            IP_Address=get_client_ip(),
            User_ID=user_id
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    if not cert:
        return render_template('verify/result.html', cert=None, certificate_number=certificate_number), 404

    return render_template('verify/result.html', cert=cert, certificate_number=certificate_number)
