import pytest
from app.services.calculation_service import calculate_operation
from app.services.price_service import get_asset_price
from app.services.export_service import export_operations
from app.models.job import ProcessingJob
from datetime import date
import io

@pytest.fixture
def mock_operation():
    return {
        "asset_code": "PETR4",
        "operation_type": "BUY",
        "quantity": 1000,
        "execution_price": 28.75
    }

def test_calculate_operation(mock_operation):
    price = mock_operation["execution_price"]
    quantity = mock_operation["quantity"]
    operation_type = mock_operation["operation_type"]

    total_value, tax_paid = calculate_operation(price, quantity, operation_type)

    # Preço × quantidade = valor total
    assert total_value == price * quantity

    # Taxa de 0.2% para compras
    assert tax_paid == pytest.approx(total_value * 0.002)

    # Teste para venda (taxa diferente)
    total_value_sell, tax_paid_sell = calculate_operation(price, quantity, "SELL")
    assert tax_paid_sell == pytest.approx(total_value_sell * 0.003)

def test_get_asset_price(mocker):
    mocker.patch('app.services.price_service.random.uniform', return_value=0)
    mocker.patch('app.services.price_service.random.randint', return_value=5)  # Evitar falha simulada

    price = get_asset_price("PETR4")
    assert price > 0

    # Diferentes ativos devem retornar diferentes preços base
    mocker.patch('app.services.price_service.random.uniform', return_value=0)
    price_vale = get_asset_price("VALE3")
    price_other = get_asset_price("OTHER")

    assert price_vale != price
    assert price_other > 0

def test_export_operations(mocker):
    # Mock para a função Operation.query
    mock_query = mocker.patch('app.models.operation.Operation.query')
    mock_filter = mock_query.filter.return_value
    mock_filter.all.return_value = [
        type('Operation', (), {
            'id': 'op_001',
            'asset_code': 'PETR4',
            'operation_type': 'BUY',
            'operation_date': date(2025, 9, 1),
            'quantity': 1000,
            'execution_price': 28.50,
            'total_value': 28500.0,
            'tax_paid': 57.0,
            'status': 'COMPLETED'
        })
    ]

    # Mock para MinIO
    mocker.patch('app.services.export_service.Minio')
    mocker.patch('app.services.export_service.io.BytesIO')

    # Mock para Flask current_app
    mock_app = mocker.patch('app.services.export_service.current_app')
    mock_app.config.get.side_effect = lambda key, default: default

    result = export_operations("FIDC001", date(2025, 9, 1), date(2025, 9, 30))
    assert "localhost:9000" in result
    assert "fidc-exports" in result
    assert "FIDC001" in result

def test_get_job_status(mocker):
    # Mock para ProcessingJob.query
    mock_query = mocker.patch('app.models.job.ProcessingJob.query')
    mock_job = type('ProcessingJob', (), {
        'job_id': 'test-job-123',
        'status': 'COMPLETED',
        'total_operations': 10,
        'processed': 8,
        'failed': 2,
        'created_at': date(2025, 9, 1),
        'completed_at': date(2025, 9, 1)
    })
    mock_query.get.return_value = mock_job

    from app.services.job_service import get_job_status
    result = get_job_status('test-job-123')

    assert result['job_id'] == 'test-job-123'
    assert result['status'] == 'COMPLETED'
    assert result['progress'] == 100.0
