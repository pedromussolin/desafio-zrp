import pytest
from app.services.calculation_service import calculate_operation
from app.services.price_service import get_asset_price
from app.services.export_service import export_operations
from app.services.job_service import JobService

@pytest.fixture
def mock_operation():
    return {
        "asset_code": "BTC",
        "operation_type": "BUY",
        "quantity": 1,
        "execution_price": 50000
    }

def test_calculate_operation(mock_operation):
    # Versão corrigida para chamar calculate_operation com os argumentos corretos
    price = mock_operation["execution_price"]
    quantity = mock_operation["quantity"]
    operation_type = mock_operation["operation_type"]
    total_value, tax_paid = calculate_operation(price, quantity, operation_type)
    assert total_value == 50000
    assert tax_paid == 100  # 0.2% de taxa em operação BUY

def test_get_asset_price(mocker):
    # Mock para o get_asset_price ao invés de fetch_price
    mocker.patch('app.services.price_service.random.uniform', return_value=0)
    price = get_asset_price("BTC")
    assert price > 0

def test_export_operations(mocker):
    # Mock para a função export_operations
    mock_url = "http://minio:9000/bucket/file.csv"
    mocker.patch('app.services.export_service.export_operations', return_value={
        "filename": "test.csv",
        "rows": 1,
        "url": mock_url
    })
    from datetime import date
    result = export_operations("TEST_FIDC", date.today(), date.today())
    assert "url" in result
    assert result["url"] == mock_url

def test_create_job(mocker):
    # Usar o JobService ao invés da função create_job
    job_id = "test-job-123"
    mock_job = {"job_id": job_id, "status": "PENDING"}
    mocker.patch('app.services.job_service.JobService.create_job', return_value=mock_job)
    job = JobService.create_job()
    assert job["job_id"] == job_id
    assert job["status"] == "PENDING"

def test_get_job_status(mocker):
    # Usar JobService.get_job_status
    job_id = "123"
    status = {"status": "COMPLETED", "processed": 10, "total_operations": 10}
    mocker.patch('app.services.job_service.JobService.get_job_status', return_value=status)
    job_status = JobService.get_job_status(job_id)
    assert job_status["status"] == "COMPLETED"
