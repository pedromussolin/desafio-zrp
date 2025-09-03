from celery import Celery, shared_task
from flask import current_app
from app import create_app, db
from app.models import Operation, Job
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

@shared_task(bind=True)
def process_operations_batch_task(self, job_id: str):
    with current_app.app_context():
        job = db.session.get(ProcessingJob, job_id)
        if not job:
            logger.error("Job not found")
            return
        ops = db.session.query(Operation).filter_by(job_id=job_id).all()
        for op in ops:
            process_operation_task.delay(op.id, job_id)
        logger.info(f"Dispatched {len(ops)} operations for job={job_id}")
