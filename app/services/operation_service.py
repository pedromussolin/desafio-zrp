from datetime import datetime, timezone
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from ..models import db
from ..models.operation import Operation
from ..models.fidc_cash import FidcCash
from ..models.job import ProcessingJob
from .price_service import get_asset_price, ExternalPriceError, RateLimitError
import logging

logger = logging.getLogger(__name__)

class OperationProcessingError(Exception):
    pass

def process_single_operation(op_id: str):
    """
    Processa uma operação (já persistida em status PENDING).
    Garante atomicidade via transação.
    """
    try:
        op: Operation = db.session.get(Operation, op_id)
        if not op:
            raise OperationProcessingError("Operation not found")
        if op.status not in ("PENDING", "FAILED"):
            return  # idempotente

        op.status = "PROCESSING"
        db.session.flush()

        fidc: FidcCash = db.session.get(FidcCash, op.fidc_id)
        if not fidc:
            raise OperationProcessingError("FIDC cash record not found")

        # Busca preço com retry simples (até 3 tentativas para falha externa, não para rate limit)
        price = None
        attempts = 0
        while attempts < 3:
            try:
                price = get_asset_price(op.asset_code)
                break
            except RateLimitError as rl:
                logger.warning(f"Rate limit - requeue? {rl}")
                raise  # deixa a task lidar
            except ExternalPriceError as e:
                attempts += 1
                logger.warning(f"Tentativa {attempts} falhou: {e}")
        if price is None:
            raise OperationProcessingError("Could not fetch price after retries")

        gross_value = op.quantity * price

        if op.operation_type == "BUY":
            tax_amount = gross_value * 0.005
            total_cost = gross_value + tax_amount
            if fidc.available_cash < total_cost:
                raise OperationProcessingError("Insufficient cash for BUY")
            fidc.available_cash -= total_cost
            op.total_value = total_cost
            op.tax_paid = tax_amount

        elif op.operation_type == "SELL":
            tax_amount = gross_value * 0.003
            net_proceeds = gross_value - tax_amount
            fidc.available_cash += net_proceeds
            op.total_value = net_proceeds
            op.tax_paid = tax_amount
        else:
            raise OperationProcessingError("Invalid operation_type")

        op.execution_price = price
        op.status = "COMPLETED"

        db.session.flush()
        logger.info(f"Operation processed id={op.id} status=COMPLETED fidc_cash={fidc.available_cash}")
        return op
    except Exception as e:
        logger.exception("Error processing operation")
        db.session.rollback()
        # Atualiza status se existir
        op = db.session.get(Operation, op_id)
        if op:
            try:
                op.status = "FAILED"
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
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
