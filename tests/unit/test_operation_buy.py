from app.models.fidc_cash import FidcCash
from app.models import db
from uuid import uuid4
from datetime import date
from app.models.job import ProcessingJob
from app.models.operation import Operation
from app.services.operation_service import process_single_operation

def test_buy_operation_reduces_cash(app):
    with app.app_context():
        fidc = FidcCash(fidc_id="F1", available_cash=100000.0)
        db.session.add(fidc)
        job = ProcessingJob(job_id=str(uuid4()), total_operations=1)
        db.session.add(job)
        op = Operation(
            id="OP1",
            fidc_id="F1",
            job_id=job.job_id,
            asset_code="TEST4",
            operation_type="BUY",
            quantity=10,
            operation_date=date.today()
        )
        db.session.add(op)
        db.session.commit()

        process_single_operation("OP1")
        db.session.refresh(op)
        db.session.refresh(fidc)
        assert op.status == "COMPLETED"
        assert op.execution_price > 0
        assert fidc.available_cash < 100000.0
