from flask import Flask, request, send_file, jsonify, render_template, Response
import os
import json
from werkzeug.utils import secure_filename
import sys
import io

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.qr_code import generate_qr_code, generate_qr_code_from_url
from utils.helpers import save_json_data, calculate_total_quantity
from api.pdf_generator import generate_pdf

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))

# Create directories for temporary files if they don't exist
os.makedirs("temp", exist_ok=True)
os.makedirs("temp/qrcodes", exist_ok=True)
os.makedirs("temp/json_data", exist_ok=True)

@app.route('/')
def root():
    return jsonify({"message": "PDF Generation Service API", "version": "1.0.0"})

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/v1/waste-transfer-act', methods=['POST'])
def generate_waste_transfer_act():
    """Generate a waste transfer act PDF document"""
    try:
        # Get JSON data from request
        data = request.json
        
        # Calculate total quantity
        total_quantity = calculate_total_quantity(data.get('wastes', []))
        
        # Add total quantity to data
        data["total_quantity"] = total_quantity
        
        # Generate QR code if requested
        if data.get('include_qr', False):
            # Save the data for verification
            json_path = save_json_data(data, "waste_transfer_act")
            qr_data = {
                "document_type": "waste_transfer_act",
                "act_number": data.get('act_number'),
                "data_path": json_path
            }
            qr_code_path = generate_qr_code(str(qr_data))
            data["qr_code_path"] = qr_code_path
        
        # Generate PDF
        output_filename = f"temp/waste_transfer_act_{data.get('act_number')}.pdf"
        pdf_path = generate_pdf(
            template_name="waste_transfer_act",
            data=data,
            output_path=output_filename
        )
        
        # Return the PDF file
        return send_file(
            pdf_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"waste_transfer_act_{data.get('act_number')}.pdf"
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/waste-removal-request', methods=['POST'])
def generate_waste_removal_request():
    """Generate a waste removal request PDF document"""
    try:
        # Get JSON data from request
        data = request.json
        
        # Calculate total quantity
        total_quantity = calculate_total_quantity(data.get('wastes', []))
        
        # Add total quantity to data
        data["total_quantity"] = total_quantity
        
        # Generate QR code if requested
        if data.get('include_qr', False):
            # Save the data for verification
            json_path = save_json_data(data, "waste_removal_request")
            qr_data = {
                "document_type": "waste_removal_request",
                "request_number": data.get('request_number'),
                "data_path": json_path
            }
            qr_code_path = generate_qr_code(str(qr_data))
            data["qr_code_path"] = qr_code_path
        
        # Generate PDF
        output_filename = f"temp/waste_removal_request_{data.get('request_number')}.pdf"
        pdf_path = generate_pdf(
            template_name="waste_removal_request",
            data=data,
            output_path=output_filename
        )
        
        # Return the PDF file
        return send_file(
            pdf_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"waste_removal_request_{data.get('request_number')}.pdf"
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/verify/<path:qr_data>')
def verify_document(qr_data):
    """Verify a document using QR code data"""
    try:
        # Parse the QR data
        qr_data = qr_data.replace("'", '"')  # Replace single quotes with double quotes for JSON parsing
        data = json.loads(qr_data)
        
        document_type = data.get("document_type")
        document_number = data.get("act_number") or data.get("request_number")
        data_path = data.get("data_path")
        
        # Check if the document data exists
        if data_path and os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                document_data = json.load(f)
                verification_status = "Документ подтвержден"
                verification_message = "Документ является подлинным и соответствует оригиналу."
        else:
            document_data = None
            verification_status = "Документ не найден"
            verification_message = "Не удалось найти данные документа. Возможно, документ был удален или изменен."
        
        # Render verification template
        return render_template(
            "verification.html",
            document_type=document_type,
            document_number=document_number,
            verification_status=verification_status,
            verification_message=verification_message,
            document_data=document_data
        )
    
    except Exception as e:
        return render_template(
            "verification.html",
            document_type="Неизвестный",
            document_number="Неизвестный",
            verification_status="Ошибка проверки",
            verification_message=f"Произошла ошибка при проверке документа: {str(e)}",
            document_data=None
        )

@app.route('/api/v1/generate-qr', methods=['GET', 'POST'])
def generate_qr_code_endpoint():
    """Generate a QR code from a URL"""
    try:
        # Get URL from request
        if request.method == 'POST':
            data = request.json
            url = data.get('url')
            size = data.get('size', 200)
            format_type = data.get('format', 'png')
        else:  # GET
            url = request.args.get('url')
            size = int(request.args.get('size', 200))
            format_type = request.args.get('format', 'png')
        
        if not url:
            return jsonify({"error": "URL parameter is required"}), 400
        
        # Generate QR code
        qr_image, qr_bytes = generate_qr_code_from_url(url, size, format_type)
        
        # Return the QR code image
        return Response(
            qr_bytes.getvalue(),
            mimetype=f"image/{format_type}",
            headers={
                "Content-Disposition": f"attachment; filename=qrcode.{format_type}"
            }
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/qr-generator', methods=['GET'])
def qr_generator_page():
    """Render a simple web page for generating QR codes"""
    return render_template('qr_generator.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
