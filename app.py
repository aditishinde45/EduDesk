import os
import datetime
from flask import Flask, render_template
from flask_login import current_user
from config import Config
from extensions import db, login_manager, csrf

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Ensure upload folders exist
    os.makedirs(app.config['CERTIFICATES_FOLDER'], exist_ok=True)
    os.makedirs(app.config['QRCODES_FOLDER'], exist_ok=True)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.departments import departments_bp
    from routes.courses import courses_bp
    from routes.certificate_types import certificate_types_bp
    from routes.authorities import authorities_bp
    from routes.students import students_bp
    from routes.certificates import certificates_bp
    from routes.revocations import revocations_bp
    from routes.users import users_bp
    from routes.audit import audit_bp
    from routes.notifications import notifications_bp
    from routes.reports import reports_bp
    from routes.verify import verify_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(certificate_types_bp)
    app.register_blueprint(authorities_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(certificates_bp)
    app.register_blueprint(revocations_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(verify_bp)

    # Global Context Processors
    @app.context_processor
    def inject_global_data():
        unread_count = 0
        if current_user.is_authenticated:
            try:
                from models import Notification
                unread_count = Notification.query.filter_by(
                    User_ID=current_user.User_ID,
                    Status='Unread'
                ).count()
            except Exception:
                unread_count = 0

        return {
            'unread_notifications_count': unread_count,
            'current_year': datetime.date.today().year,
            'now': datetime.datetime.now()
        }

    # Custom Error Pages
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print(f"\n=======================================================")
    print(f" EduDesk - Certificate Management System")
    print(f" K. K. Wagh Institute of Engineering Education & Research")
    print(f" Running on http://127.0.0.1:{port} (http://localhost:{port})")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=True)
