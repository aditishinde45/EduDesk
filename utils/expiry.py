import datetime
from extensions import db
from models import Certificate
from utils.notifications import notify_student_certificate

def check_and_update_expired_certificates():
    """
    Auto-expiry check: whenever certificates are loaded (or on request/scheduled),
    updates Status = 'Expired' where Expiry_Date < today and Status = 'Active'.
    Also sends notification to student about expiration.
    """
    today = datetime.date.today()
    expired_certs = Certificate.query.filter(
        Certificate.Expiry_Date.isnot(None),
        Certificate.Expiry_Date < today,
        Certificate.Status == 'Active'
    ).all()

    updated_count = 0
    for cert in expired_certs:
        cert.Status = 'Expired'
        updated_count += 1
        notify_student_certificate(
            cert.Student_ID,
            f"Your certificate '{cert.Certificate_Name}' ({cert.Certificate_Number}) expired on {cert.Expiry_Date}."
        )

    if updated_count > 0:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"[Auto-Expiry Commit Error]: {e}")

    return updated_count


def check_expiring_soon_certificates():
    """
    Finds certificates expiring within 30 days and sends a warning notification if active.
    """
    today = datetime.date.today()
    warning_date = today + datetime.timedelta(days=30)
    expiring_soon = Certificate.query.filter(
        Certificate.Expiry_Date.isnot(None),
        Certificate.Expiry_Date >= today,
        Certificate.Expiry_Date <= warning_date,
        Certificate.Status == 'Active'
    ).all()

    for cert in expiring_soon:
        notify_student_certificate(
            cert.Student_ID,
            f"Reminder: Your certificate '{cert.Certificate_Name}' ({cert.Certificate_Number}) is scheduled to expire on {cert.Expiry_Date}."
        )
