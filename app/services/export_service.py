import csv
import io
from datetime import datetime, timezone
from minio import Minio
from minio.error import S3Error
from flask import current_app
from app.models import db
from app.models.operation import Operation
import logging

logger = logging.getLogger(__name__)

def _client():
    return Minio(
        current_app.config["S3_ENDPOINT"],
        access_key=current_app.config["S3_ACCESS_KEY"],
        secret_key=current_app.config["S3_SECRET_KEY"],
        secure=current_app.config["S3_SECURE"],
    )

def _ensure_bucket(client, bucket):
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

def export_operations(fidc_id: str, start_date, end_date):
    q = (
        db.session.query(Operation)
        .filter(
            Operation.fidc_id == fidc_id,
            Operation.operation_date >= start_date,
            Operation.operation_date <= end_date,
            Operation.status == "COMPLETED"
        )
        .order_by(Operation.operation_date)
    )
    rows = q.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id","fidc_id","asset_code","type","qty","date","price","total","tax"])
    for r in rows:
        writer.writerow([
            r.id, r.fidc_id, r.asset_code, r.operation_type, r.quantity,
            r.operation_date.isoformat(), r.execution_price, r.total_value, r.tax_paid
        ])

    content = output.getvalue().encode()
    filename = f"{fidc_id}/export_{fidc_id}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}.csv"

    client = _client()
    bucket = current_app.config["S3_BUCKET"]
    _ensure_bucket(client, bucket)

    client.put_object(
        bucket_name=bucket,
        object_name=filename,
        data=io.BytesIO(content),
        length=len(content),
        content_type="text/csv"
    )

    # Presigned URL (expira em 1 hora)
    url = client.get_presigned_url("GET", bucket, filename, expires=3600)
    logger.info(f"Export uploaded bucket={bucket} object={filename}")
    return {"filename": filename, "rows": len(rows), "url": url}
