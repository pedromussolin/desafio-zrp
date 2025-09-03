from flask import Blueprint, request, jsonify
from app.services.export_service import export_operations_to_bucket
from app.models.job import Job
from app import db

exports_bp = Blueprint('exports', __name__)

@exports_bp.route('/operations/export', methods=['POST'])
def export_operations():
    data = request.get_json()
    if not data or 'operation_ids' not in data:
        return jsonify({'error': 'Invalid request, operation_ids required'}), 400

    operation_ids = data['operation_ids']
    job = Job(status='pending')
    db.session.add(job)
    db.session.commit()

    # Trigger the export task asynchronously
    export_task = export_operations_to_bucket.delay(operation_ids, job.job_id)

    return jsonify({'job_id': job.job_id, 'task_id': export_task.id}), 202