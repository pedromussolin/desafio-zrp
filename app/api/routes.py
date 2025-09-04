from flask import Blueprint, request, jsonify, current_app
from marshmallow import Schema, fields, validate
from app.models.operation import Operation
from app.models.job import ProcessingJob
from app.models.fidc_cash import FidcCash
from app.tasks.operation_tasks import process_operations_batch_task
from app.services.export_service import export_operations
from app.services.job_service import get_job_status
import uuid
import logging
from datetime import datetime, timezone
from ..models import db
from .schemas import ProcessOperationsSchema, ExportSchema

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)

# Esquema de validação para operações
class OperationSchema(Schema):
    id = fields.String(required=True)
    asset_code = fields.String(required=True)
    operation_type = fields.String(required=True, validate=validate.OneOf(["BUY", "SELL"]))
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    operation_date = fields.Date(required=True)

class OperationBatchSchema(Schema):
    fidc_id = fields.String(required=True)
    operations = fields.List(fields.Nested(OperationSchema), required=True)

class ExportSchema(Schema):
    fidc_id = fields.String(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

@api_bp.route('/jobs/test/status', methods=['GET'])
def test_status():
    """Simple test endpoint"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    })

@api_bp.route("/operations/process", methods=["POST"])
def process_operations():
    """
    Endpoint to process a batch of operations
    """
    try:
        # Validate request data
        schema = OperationBatchSchema()
        data = schema.load(request.json)

        fidc_id = data["fidc_id"]
        operations = data["operations"]

        # Create job
        job_id = str(uuid.uuid4())
        job = ProcessingJob(
            job_id=job_id,
            status="PROCESSING",
            total_operations=len(operations),
            estimated_completion=datetime.utcnow()
        )
        db.session.add(job)

        # Create operations in DB
        op_ids = []
        for op_data in operations:
            operation = Operation(
                id=op_data["id"],
                fidc_id=fidc_id,
                job_id=job_id,
                asset_code=op_data["asset_code"],
                operation_type=op_data["operation_type"],
                quantity=op_data["quantity"],
                operation_date=op_data["operation_date"]
            )
            db.session.add(operation)
            op_ids.append(op_data["id"])

        db.session.commit()

        # Send to celery processing
        process_operations_batch_task.delay(job_id, op_ids)

        return jsonify({
            "job_id": job_id,
            "message": "Operations submitted for processing",
            "total_operations": len(operations)
        }), 202

    except Exception as e:
        logger.error(f"Error in process_operations: {str(e)}")
        return jsonify({"error": str(e)}), 400

@api_bp.route("/jobs/<job_id>/status", methods=["GET"])
def job_status(job_id):
    """
    Get job status
    """
    status = get_job_status(job_id)
    if not status:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(status), 200

@api_bp.route("/operations/export", methods=["POST"])
def export_operations_route():
    """
    Export operations to CSV
    """
    try:
        # Validate request data
        schema = ExportSchema()
        data = schema.load(request.json)

        fidc_id = data["fidc_id"]
        start_date = data["start_date"]
        end_date = data["end_date"]

        # Export operations
        result = export_operations(fidc_id, start_date, end_date)

        return jsonify({
            "message": "Export successful",
            "download_url": result
        }), 200

    except Exception as e:
        logger.error(f"Error in export_operations: {str(e)}")
        return jsonify({"error": str(e)}), 400
