import datetime
from flask_login import current_user
from extensions import db
from models import AuditLog
from utils.helpers import get_client_ip

def log_audit(action, user_id=None, ip_address=None):
    """
    Records an entry in the Audit_Log table.
    """
    try:
        if user_id is None:
            if current_user and current_user.is_authenticated:
                user_id = current_user.User_ID
            else:
                return  # Cannot log action without associated User_ID due to NOT NULL FK

        if ip_address is None:
            ip_address = get_client_ip()

        audit = AuditLog(
            Action=action[:100],
            Timestamp=datetime.datetime.now(datetime.timezone.utc),
            IP_Address=ip_address,
            User_ID=user_id
        )
        db.session.add(audit)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Keep application resilient even if audit log fails
        print(f"[AuditLog Error]: {e}")
