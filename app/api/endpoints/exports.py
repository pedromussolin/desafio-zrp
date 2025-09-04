from flask import Blueprint, request, jsonify
from app.services.export_service import export_operations
from app.models.job import Job
from app import db
from datetime import datetime

exports_bp = Blueprint('exports', __name__)

@exports_bp.route('/operations/export', methods=['POST'])
def export_operations_endpoint():
    data = request.get_json()
    if not data or not all(k in data for k in ['fidc_id', 'start_date', 'end_date']):
        return jsonify({'error': 'Invalid request, fidc_id, start_date and end_date required'}), 400

    fidc_id = data['fidc_id']
    start_date = datetime.fromisoformat(data['start_date']).date()
    end_date = datetime.fromisoformat(data['end_date']).date()

    # Export operations directly
    try:
        result = export_operations(fidc_id, start_date, end_date)
        return jsonify({
            "filename": result["filename"],
            "rows": result["rows"],
            "download_url": result["url"]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
