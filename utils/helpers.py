import os
import uuid
from flask import request, current_app
from werkzeug.utils import secure_filename

def get_client_ip():
    """Extract client IP address safely, respecting reverse proxies if any."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']


def save_uploaded_certificate(file):
    """
    Saves an uploaded certificate file securely to static/uploads/certificates.
    Returns relative path from static folder: uploads/certificates/<filename>
    """
    if not file or not allowed_file(file.filename):
        return None

    filename = secure_filename(file.filename)
    unique_suffix = uuid.uuid4().hex[:8]
    ext = filename.rsplit('.', 1)[1].lower()
    base_name = filename.rsplit('.', 1)[0][:30]
    safe_name = f"{base_name}_{unique_suffix}.{ext}"

    dest_folder = current_app.config['CERTIFICATES_FOLDER']
    os.makedirs(dest_folder, exist_ok=True)
    full_path = os.path.join(dest_folder, safe_name)
    file.save(full_path)

    # Return relative path for web and database storage
    return f"uploads/certificates/{safe_name}"
