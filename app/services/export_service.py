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

    logger.info(f"Found {len(operations)} operations to export")

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
            op.operation_date.strftime("%Y-%m-%d") if op.operation_date else "",
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
        # Get MinIO configuration with fallbacks
        endpoint = current_app.config.get("MINIO_ENDPOINT", "minio:9000")
        access_key = current_app.config.get("MINIO_ACCESS_KEY", "minioadmin")
        secret_key = current_app.config.get("MINIO_SECRET_KEY", "minioadmin")
        bucket_name = current_app.config.get("MINIO_BUCKET", "fidc-exports")

        logger.info(f"Connecting to MinIO at {endpoint}")

        # Connect to MinIO
        minio_client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False  # For development (http)
        )

        # Make bucket if not exists
        if not minio_client.bucket_exists(bucket_name):
            logger.info(f"Creating bucket: {bucket_name}")
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

        # Generate URLs - one for internal use, one for browser access
        internal_url = f"http://{endpoint}/{bucket_name}/{object_name}"
        external_url = f"http://localhost:9000/{bucket_name}/{object_name}"  # Use a porta mapeada no host

        logger.info(f"Exported operations for FIDC {fidc_id}")
        logger.info(f"Internal URL: {internal_url}")
        logger.info(f"Browser URL: {external_url}")

        return external_url

    except Exception as e:
        logger.error(f"Error exporting to MinIO: {str(e)}")
        raise Exception(f"Failed to export operations: {str(e)}")
