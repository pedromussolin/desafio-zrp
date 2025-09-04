from celery import Celery, shared_task
from flask import current_app
from app import create_app, db
from app.models.operation import Operation
from app.models.job import Job
from app.services.calculation_service import calculate_operation
from app.services.job_service import create_job
from ..models.job import ProcessingJob
from ..models.fidc_cash import FidcCash
from ..services.operation_service import process_single_operation, update_job_progress, OperationProcessingError
from ..services.price_service import RateLimitError
import logging
import time

logger = logging.getLogger(__name__)

app = create_app()
celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@shared_task(bind=True, autoretry_for=(RateLimitError,), retry_backoff=10, retry_kwargs={"max_retries": 5})
def process_operation_task(self, operation_id: str, job_id: str):
    with current_app.app_context():
        try:
            process_single_operation(operation_id)
            update_job_progress(job_id)
        except RateLimitError as rl:
            logger.warning(f"Rate limited op={operation_id}, retrying: {rl}")
            raise
        except OperationProcessingError as e:
            logger.error(f"Business error on operation {operation_id}: {e}")
            update_job_progress(job_id)
        except Exception as e:
            logger.exception(f"Unexpected error op={operation_id}")
            update_job_progress(job_id)
            raise

@shared_task
def process_operations_batch_task(job_id, ops_ids):
    """
    Process a batch of operations
    """
    try:
        logger.info(f"Starting batch processing for job_id={job_id}, ops_count={len(ops_ids)}")
        for op_id in ops_ids:
            try:
                process_single_operation(op_id)
            except Exception as e:
                logger.error(f"Failed to process operation {op_id}: {str(e)}")

        logger.info(f"Completed batch processing for job_id={job_id}")
    except Exception as e:
        logger.error(f"Batch processing failed for job_id={job_id}: {str(e)}")
        raise
