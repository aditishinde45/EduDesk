import os
import qrcode
from flask import current_app

def generate_certificate_qr(certificate_number, verify_url=None):
    """
    Generates a QR code PNG image that encodes the certificate verification URL.
    Saves to static/uploads/qrcodes/qr_<certificate_number>.png
    Returns relative path: uploads/qrcodes/qr_<certificate_number>.png
    """
    if not verify_url:
        verify_url = f"/verify/{certificate_number}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0d6efd", back_color="white")

    qrcodes_folder = current_app.config['QRCODES_FOLDER']
    os.makedirs(qrcodes_folder, exist_ok=True)

    # Sanitize certificate number for safe filename
    safe_number = "".join(c for c in certificate_number if c.isalnum() or c in ('-', '_'))
    filename = f"qr_{safe_number}.png"
    full_path = os.path.join(qrcodes_folder, filename)
    img.save(full_path)

    return f"uploads/qrcodes/{filename}"
