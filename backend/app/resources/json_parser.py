from flask import Blueprint, request, jsonify, g, current_app
from app.utils.auth import token_required
from app.models.pdf.test_service import run_tests
from app.extensions import db  # Make sure you have this import
import json
import os

bp = Blueprint('json_parser', __name__, url_prefix='/api')


# Add this model if you don't have it already
class FilePath(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(50), unique=True, nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


@bp.route('/api/get-file-path/<string:request_number>', methods=['GET'])
@token_required
def get_file_path(request_number):
    try:
        # Query the database for the file path
        file_record = FilePath.query.filter_by(request_number=request_number).first()

        if not file_record:
            return jsonify({
                "error": f"No file path found for request {request_number}"
            }), 404

        # Verify the file exists
        if not os.path.exists(file_record.file_path):
            return jsonify({
                "error": "File not found at the specified path",
                "path": file_record.file_path
            }), 404

        return jsonify({
            "success": True,
            "request_number": request_number,
            "file_path": file_record.file_path,
            "absolute_path": os.path.abspath(file_record.file_path),
            "file_exists": True,
            "processed_by": g.current_user.username
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('api/parsejson', methods=['POST'])
@token_required
def parse_json():
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Example parsing operation (you can customize this)
        parsed_data = {
            "original": data,
            "keys": list(data.keys()),
            "values": list(data.values()),
            "size": len(str(data)),
            "processed_by": g.current_user.username
        }
        run_tests()

        return jsonify({
            "success": True,
            "result": parsed_data
        })

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def parse_json():
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Transform the data into the required format
        parsed_data = {
            "request_number": data.get("request_number"),
            "request_date": data.get("request_date"),
            "requester": {
                "name": data.get("requester", {}).get("name"),
                "inn": data.get("requester", {}).get("inn"),
                "address": data.get("requester", {}).get("address"),
                "contact_person": data.get("requester", {}).get("contact_person"),
                "phone": data.get("requester", {}).get("phone"),
                "representative": {
                    "name": data.get("requester", {}).get("representative", {}).get("name"),
                    "position": data.get("requester", {}).get("representative", {}).get("position")
                }
            },
            "contract": {
                "number": data.get("contract", {}).get("number"),
                "date": data.get("contract", {}).get("date")
            },
            "pickup_address": data.get("pickup_address"),
            "preferred_date": data.get("preferred_date"),
            "preferred_time": data.get("preferred_time"),
            "wastes": [
                {
                    "name": waste.get("name"),
                    "code": waste.get("code"),
                    "hazard_class": waste.get("hazard_class"),
                    "quantity": float(waste.get("quantity", 0)) if waste.get("quantity") else 0.0,
                    "packaging": waste.get("packaging")
                } for waste in data.get("wastes", [])
            ],
            "status": data.get("status"),
            "special_requirements": data.get("special_requirements"),
            "additional_info": data.get("additional_info"),
            "operator": {
                "name": data.get("operator", {}).get("name"),
                "position": data.get("operator", {}).get("position")
            },
            "approval_date": data.get("approval_date"),
            "include_qr": bool(data.get("include_qr", False)),
            "qr_url": data.get("qr_url")
        }

        # Optional: Validate required fields
        required_fields = [
            "request_number", "request_date",
            ("requester", "name"), ("requester", "inn"),
            ("contract", "number"), "pickup_address"
        ]

        errors = []
        for field in required_fields:
            if isinstance(field, tuple):
                # Nested field check
                value = parsed_data
                for subfield in field:
                    value = value.get(subfield, {})
                if not value:
                    errors.append(f"Missing required field: {'->'.join(field)}")
            else:
                if not parsed_data.get(field):
                    errors.append(f"Missing required field: {field}")

        if errors:
            return jsonify({
                "error": "Validation failed",
                "details": errors
            }), 400

        run_tests()
        # url from db in progress
        return jsonify({
            "success": True,
            "result": parsed_data
        })

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except ValueError as e:
        return jsonify({"error": f"Invalid value: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
