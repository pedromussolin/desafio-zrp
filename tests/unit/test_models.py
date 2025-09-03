from app.models.operation import Operation
from app.models.job import Job
from app import db
import pytest

@pytest.fixture
def operation():
    op = Operation(
        asset_code='BTC',
        operation_type='BUY',
        quantity=1.5,
        status='PENDING',
        execution_price=50000,
        total_value=75000,
        tax_paid=0,
    )
    db.session.add(op)
    db.session.commit()
    yield op
    db.session.delete(op)
    db.session.commit()

def test_operation_creation(operation):
    assert operation.id is not None
    assert operation.asset_code == 'BTC'
    assert operation.operation_type == 'BUY'
    assert operation.quantity == 1.5
    assert operation.status == 'PENDING'
    assert operation.execution_price == 50000
    assert operation.total_value == 75000
    assert operation.tax_paid == 0

def test_job_creation():
    job = Job(status='COMPLETED')
    db.session.add(job)
    db.session.commit()
    
    assert job.job_id is not None
    assert job.status == 'COMPLETED'
    assert job.created_at is not None
    assert job.completed_at is None

    db.session.delete(job)
    db.session.commit()