from flask import Blueprint, jsonify
from app.services.job_service import JobService

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/jobs/<string:job_id>/status', methods=['GET'])
def get_job_status(job_id):
    job_status = JobService.get_job_status(job_id)
    if job_status is None:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify({'job_id': job_id, 'status': job_status})