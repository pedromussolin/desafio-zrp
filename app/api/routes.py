from flask import Blueprint, request, jsonify, current_app
from marshmallow import Schema, fields, validate
from app.models.operation import Operation
from app.models.job import ProcessingJob
from app.models.fidc_cash import FidcCash
from app.tasks.operation_tasks import process_operations_batch_task
from app.services.export_service import export_operations
import uuid
import logging

from uuid import uuid4
from datetime import datetime, timezone
from ..models import db
from .schemas import ProcessOperationsSchema, ExportSchema

api_bp = Blueprint("api", __name__)

@api_bp.route("/operations/process", methods=["POST"])
def process_operations():
    payload = request.get_json() or {}
    errors = ProcessOperationsSchema().validate(payload)
    if errors:
        return jsonify({"errors": errors}), 400

    fidc_id = payload["fidc_id"]
    ops = payload["operations"]

    # Garante que o FIDC existe (ou cria para demo)
    fidc = db.session.get(FidcCash, fidc_id)
    if not fidc:
        fidc = FidcCash(fidc_id=fidc_id, available_cash=1_000_000.0)
        db.session.add(fidc)

    job_id = str(uuid4())
    job = ProcessingJob(job_id=job_id, status="PROCESSING", total_operations=len(ops))
    db.session.add(job)

    # Persiste operações
    for op in ops:
        db.session.add(
            Operation(
                id=op["id"],
                fidc_id=fidc_id,
                job_id=job_id,
                asset_code=op["asset_code"],
                operation_type=op["operation_type"],
                quantity=op["quantity"],
                operation_date=op["operation_date"],
                status="PENDING"
            )
        )
    db.session.commit()

    process_operations_batch_task.delay(job_id)

    return jsonify({"job_id": job_id, "status": "ENQUEUED"}), 202

@api_bp.route("/jobs/<job_id>/status", methods=["GET"])
def job_status(job_id):
    job = db.session.get(ProcessingJob, job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    # Estimativa simples
    processed_count = job.processed + job.failed
    eta = None
    if processed_count and job.total_operations and processed_count < job.total_operations:
        # naive: tempo médio = (agora - created)/processed * restante
        elapsed = (datetime.now(timezone.utc) - job.created_at).total_seconds()
        avg_per_op = elapsed / processed_count
        remaining = (job.total_operations - processed_count) * avg_per_op
        eta = datetime.now(timezone.utc).timestamp() + remaining

    return jsonify({
        "job_id": job.job_id,
        "status": job.status,
        "total_operations": job.total_operations,
        "processed": job.processed,
        "failed": job.failed,
        "estimated_completion": datetime.fromtimestamp(eta, tz=timezone.utc).isoformat() if eta else None
    })

@api_bp.route("/operations/export", methods=["POST"])
def export_ops():
    payload = request.get_json() or {}
    errors = ExportSchema().validate(payload)
    if errors:
        return jsonify({"errors": errors}), 400
    result = export_operations(payload["fidc_id"], payload["start_date"], payload["end_date"])
    return jsonify({
        "filename": result["filename"],
        "rows": result["rows"],
        "download_url": result["url"]
    })
