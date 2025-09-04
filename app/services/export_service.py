import csv
import io
from datetime import datetime
import os
from minio import Minio
from minio.error import S3Error
from flask import current_app
from app.models import db
from app.models.operation import Operation
import logging

logger = logging.getLogger(__name__)

def export_operations(fidc_id, start_date, end_date):
    """
    Export operations to CSV and upload to MinIO

    Args:
        fidc_id (str): FIDC ID
        start_date (date): Start date for filtering operations
        end_date (date): End date for filtering operations

    Returns:
        str: URL to download the exported file
    """
    # Query operations
    operations = Operation.query.filter(
        Operation.fidc_id == fidc_id,
        Operation.operation_date >= start_date,
        Operation.operation_date <= end_date,
        Operation.status == "COMPLETED"
    ).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "ID", "Asset", "Type", "Date", "Quantity",
        "Price", "Total Value", "Tax Paid", "Status"
    ])

    # Write data
    for op in operations:
        writer.writerow([
            op.id,
            op.asset_code,
            op.operation_type,
            op.operation_date.strftime("%Y-%m-%d"),
            op.quantity,
            op.execution_price,
            op.total_value,
            op.tax_paid,
            op.status
        ])

    # Get CSV content
    csv_content = output.getvalue()

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{fidc_id}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{timestamp}.csv"

    # Upload to MinIO
    try:
        # Connect to MinIO
        minio_client = Minio(
            current_app.config["MINIO_ENDPOINT"],
            access_key=current_app.config["MINIO_ACCESS_KEY"],
            secret_key=current_app.config["MINIO_SECRET_KEY"],
            secure=False  # For development (http)
        )

        # Make bucket if not exists
        bucket_name = current_app.config["MINIO_BUCKET"]
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        # Create object path
        object_name = f"{fidc_id}/{filename}"

        # Upload CSV
        csv_bytes = csv_content.encode('utf-8')
        csv_buffer = io.BytesIO(csv_bytes)

        minio_client.put_object(
            bucket_name,
            object_name,
            data=csv_buffer,
            length=len(csv_bytes),
            content_type="text/csv"
        )

        # Generate URL
        url = f"http://{current_app.config['MINIO_ENDPOINT']}/{bucket_name}/{object_name}"

        logger.info(f"Exported operations for FIDC {fidc_id} to {url}")
        return url

    except S3Error as e:
        logger.error(f"Error uploading to MinIO: {str(e)}")
        raise Exception("Failed to upload export file")
