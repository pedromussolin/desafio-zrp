import csv
import io
from datetime import datetime, timezone
from flask import current_app
import boto3
import pandas as pd
from app.models import Operation
from ..models import db
from ..models.operation import Operation
import logging

logger = logging.getLogger(__name__)

class ExportService:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = current_app.config['S3_BUCKET_NAME']

    def export_operations(self, operations):
        if not operations:
            return None

        # Convert operations to DataFrame
        df = pd.DataFrame([op.to_dict() for op in operations])

        # Create a CSV file from the DataFrame
        csv_file_path = '/tmp/operations_export.csv'
        df.to_csv(csv_file_path, index=False)

        # Upload the CSV file to S3
        self.upload_to_s3(csv_file_path)

        return csv_file_path

    def upload_to_s3(self, file_path):
        with open(file_path, 'rb') as data:
            self.s3_client.upload_fileobj(data, self.bucket_name, 'exports/operations_export.csv')

def export_operations(fidc_id: str, start_date, end_date):
    """
    Stub: gera CSV em memória (integração S3 será feita depois).
    """
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
    writer.writerow(["id", "fidc_id", "asset_code", "type", "qty", "date", "price", "total", "tax"])
    for r in rows:
        writer.writerow([
            r.id, r.fidc_id, r.asset_code, r.operation_type, r.quantity,
            r.operation_date.isoformat(), r.execution_price, r.total_value, r.tax_paid
        ])

    content = output.getvalue()
    filename = f"export_{fidc_id}_{datetime.now(timezone.utc).isoformat()}.csv"
    logger.info(f"Generated export {filename} bytes={len(content)}")
    return {"filename": filename, "bytes": len(content), "content": content}
