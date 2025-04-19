import os
import qrcode
from typing import Optional, Tuple
from io import BytesIO
from PIL import Image

def generate_qr_code(data: str, size: int = 200) -> str:
    """
    Generate a QR code image from the provided data.
    
    Args:
        data: String data to encode in the QR code
        size: Size of the QR code image in pixels
    
    Returns:
        Path to the generated QR code image
    """
    # Create directory for QR codes if it doesn't exist
    qr_dir = os.path.join("temp", "qrcodes")
    os.makedirs(qr_dir, exist_ok=True)
    
    # Generate a unique filename based on the data
    filename = f"qrcode_{hash(data)}.png"
    output_path = os.path.join(qr_dir, filename)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the image
    img.save(output_path)
    
    return output_path

def generate_qr_code_from_url(url: str, size: int = 200, format_type: str = 'png') -> Tuple[Image.Image, BytesIO]:
    """
    Generate a QR code image from a URL and return it as an image and bytes.
    
    Args:
        url: URL to encode in the QR code
        size: Size of the QR code image in pixels
        format_type: Image format (png, jpg, etc.)
    
    Returns:
        Tuple containing the PIL Image and BytesIO object with image data
    """
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Resize if needed
    if img.size[0] != size:
        img = img.resize((size, size))
    
    # Save to BytesIO
    img_bytes = BytesIO()
    img.save(img_bytes, format=format_type.upper())
    img_bytes.seek(0)
    
    return img, img_bytes

def verify_qr_code(qr_data: str) -> Optional[dict]:
    """
    Verify the data encoded in a QR code.
    
    Args:
        qr_data: String data decoded from the QR code
    
    Returns:
        Dictionary with verification result or None if verification fails
    """
    try:
        # In a real-world scenario, this would verify the data against a database
        # or other source of truth. For this example, we'll just return the decoded data.
        import json
        return json.loads(qr_data)
    except Exception:
        return None
