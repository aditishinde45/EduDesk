import datetime
from extensions import db
from models import Notification, User, Student

def create_notification(user_id, message):
    """
    Creates a new Notification for a specified user.
    """
    try:
        if not user_id:
            return None
        notif = Notification(
            Message=message,
            Sent_Date=datetime.datetime.utcnow(),
            Status='Unread',
            User_ID=user_id
        )
        db.session.add(notif)
        db.session.commit()
        return notif
    except Exception as e:
        db.session.rollback()
        print(f"[Notification Error]: {e}")
        return None


def notify_student_certificate(student_id, message):
    """
    Finds the user account associated with a student and creates a notification.
    """
    student = Student.query.get(student_id)
    if not student:
        return None

    # Try finding User with direct Student_ID or matching Email
    user = User.query.filter((User.Student_ID == student_id) | (User.Email == student.Email)).first()
    if user:
        return create_notification(user.User_ID, message)
    return None


def notify_admins(message):
    """
    Sends a notification to all Admin users.
    """
    admins = User.query.filter_by(Role='Admin').all()
    count = 0
    for admin in admins:
        if create_notification(admin.User_ID, message):
            count += 1
    return count
