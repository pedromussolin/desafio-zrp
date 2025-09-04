from datetime import datetime, timezone
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from app.models import db
from app.models.operation import Operation
from app.models.fidc_cash import FidcCash
from app.models.job import ProcessingJob
from app.services.price_service import get_asset_price, ExternalPriceError, RateLimitError
from app.services.calculation_service import calculate_operation
import logging

logger = logging.getLogger(__name__)

class OperationProcessingError(Exception):
    pass

def process_single_operation(operation_id):
    """
    Process a single operation
    """
    operation = Operation.query.get(operation_id)
    if not operation:
        logger.error(f"Operation {operation_id} not found")
        return

    if operation.status != "PENDING":
        logger.info(f"Operation {operation_id} not in PENDING state (current: {operation.status}), skipping")
        return

    # Mark as processing
    operation.status = "PROCESSING"
    db.session.commit()

    try:
        # Get price from "external" API
        price = get_asset_price(operation.asset_code)

        # Calculate values
        total_value, tax_paid = calculate_operation(
            price, operation.quantity, operation.operation_type
        )

        # Update fidc cash
        fidc = FidcCash.query.get(operation.fidc_id)
        if not fidc:
            fidc = FidcCash(fidc_id=operation.fidc_id)
            db.session.add(fidc)

        # For BUY operations, we need to check if there's enough cash
        if operation.operation_type == "BUY":
            if fidc.available_cash < total_value + tax_paid:
                logger.error(f"Not enough cash for operation {operation_id}")
                operation.status = "FAILED"
                db.session.commit()
                return

            fidc.available_cash -= (total_value + tax_paid)
        else:  # SELL
            fidc.available_cash += (total_value - tax_paid)

        # Update operation
        operation.status = "COMPLETED"
        operation.execution_price = price
        operation.total_value = total_value
        operation.tax_paid = tax_paid

        # Update job progress
        job = ProcessingJob.query.get(operation.job_id)
        if job:
            job.processed += 1
            if job.processed + job.failed >= job.total_operations:
                job.status = "COMPLETED"
                job.completed_at = datetime.utcnow()

        db.session.commit()
        logger.info(f"Operation {operation_id} processed successfully")

    except Exception as e:
        logger.error(f"Error processing operation {operation_id}: {str(e)}")
        operation.status = "FAILED"

        # Update job progress for failed operation
        job = ProcessingJob.query.get(operation.job_id)
        if job:
            job.failed += 1
            if job.processed + job.failed >= job.total_operations:
                job.status = "COMPLETED"
                job.completed_at = datetime.utcnow()

        db.session.commit()
        raise

def update_job_progress(job_id: str):
    job: ProcessingJob = db.session.get(ProcessingJob, job_id)
    if not job:
        return
    processed = db.session.query(Operation).filter_by(job_id=job_id, status="COMPLETED").count()
    failed = db.session.query(Operation).filter_by(job_id=job_id, status="FAILED").count()
    job.processed = processed
    job.failed = failed
    if (processed + failed) >= job.total_operations:
        job.status = "COMPLETED" if failed == 0 else "FAILED"
        job.completed_at = datetime.now(timezone.utc)
    db.session.commit()
