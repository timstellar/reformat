from flask import Flask, request, jsonify, render_template, send_file, Response
import os
import json
from datetime import datetime
import uuid
from api.pdf_generator import generate_pdf
from utils.qr_code import generate_qr_code_for_pdf, generate_qr_code_from_url

app = Flask(__name__)

# Create temp directory if it doesn't exist
os.makedirs("temp", exist_ok=True)

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "PDF Generation Service API", "version": "1.0.0"})

@app.route("/", methods=["GET"])
def index():
    """API root endpoint"""
    return jsonify({"message": "PDF Generation Service API", "version": "1.0.0"})

@app.route("/api/v1/waste-transfer-act", methods=["POST"])
def generate_waste_transfer_act():
    """Generate a waste transfer act PDF"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Calculate total quantity
        total_quantity = sum(waste.get("quantity", 0) for waste in data.get("wastes", []))
        data["total_quantity"] = total_quantity
        
        # Generate QR code for URL if provided
        if "qr_url" in data:
            qr_url_code_path = generate_qr_code_for_pdf(data["qr_url"], size=300)
            data["qr_url_code_path"] = qr_url_code_path
        
        # Generate PDF
        output_filename = f"waste_transfer_act_{uuid.uuid4()}.pdf"
        output_path = os.path.join("temp", output_filename)
        
        generate_pdf("waste_transfer_act", data, output_path)
        
        # Return the PDF
        return send_file(output_path, mimetype="application/pdf", as_attachment=True, 
                         download_name=f"waste_transfer_act_{data.get('act_number', 'unknown')}.pdf")
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/waste-removal-request", methods=["POST"])
def generate_waste_removal_request():
    """Generate a waste removal request PDF"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Calculate total quantity
        total_quantity = sum(waste.get("quantity", 0) for waste in data.get("wastes", []))
        data["total_quantity"] = total_quantity
        
        # Generate QR code for URL if provided
        if "qr_url" in data:
            qr_url_code_path = generate_qr_code_for_pdf(data["qr_url"], size=300)
            data["qr_url_code_path"] = qr_url_code_path
        
        # Generate PDF
        output_filename = f"waste_removal_request_{uuid.uuid4()}.pdf"
        output_path = os.path.join("temp", output_filename)
        
        generate_pdf("waste_removal_request", data, output_path)
        
        # Return the PDF
        return send_file(output_path, mimetype="application/pdf", as_attachment=True, 
                         download_name=f"waste_removal_request_{data.get('request_number', 'unknown')}.pdf")
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/generate-qr", methods=["GET", "POST"])
def generate_qr():
    """Generate a QR code image from a URL"""
    try:
        if request.method == "POST":
            # Get JSON data from request
            data = request.get_json()
            url = data.get("url")
            size = data.get("size", 200)
            format_type = data.get("format", "png")
        else:
            # Get parameters from query string
            url = request.args.get("url")
            size = int(request.args.get("size", 200))
            format_type = request.args.get("format", "png")
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        # Generate QR code
        _, img_bytes = generate_qr_code_from_url(url, size, format_type)
        
        # Return the image
        return Response(img_bytes.getvalue(), mimetype=f"image/{format_type}")
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/qr-generator", methods=["GET"])
def qr_generator_page():
    """QR code generator web page"""
    return render_template("qr_generator.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
