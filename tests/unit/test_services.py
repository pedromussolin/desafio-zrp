from app.services.calculation_service import calculate_operation
from app.services.price_service import fetch_price
from app.services.export_service import export_operations
from app.services.job_service import create_job, get_job_status
import pytest

@pytest.fixture
def mock_operation():
    return {
        "asset_code": "BTC",
        "operation_type": "BUY",
        "quantity": 1,
        "execution_price": 50000
    }

def test_calculate_operation(mock_operation):
    result = calculate_operation(mock_operation)
    assert result['total_value'] == 50000
    assert result['tax_paid'] == 0  # Assuming no tax for simplicity

def test_fetch_price(mocker):
    mocker.patch('app.services.price_service.requests.get', return_value=mocker.Mock(status_code=200, json=lambda: {"price": 50000}))
    price = fetch_price("BTC")
    assert price == 50000

def test_export_operations(mocker):
    mocker.patch('app.services.export_service.upload_to_bucket', return_value=True)
    result = export_operations([{"id": 1, "asset_code": "BTC", "quantity": 1}])
    assert result is True

def test_create_job(mocker):
    mocker.patch('app.services.job_service.save_job', return_value={"job_id": "123", "status": "created"})
    job = create_job("export", {"asset_code": "BTC"})
    assert job['job_id'] == "123"
    assert job['status'] == "created"

def test_get_job_status(mocker):
    mocker.patch('app.services.job_service.get_job', return_value={"job_id": "123", "status": "completed"})
    job_status = get_job_status("123")
    assert job_status['status'] == "completed"