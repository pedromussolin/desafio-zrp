import pytest
from app import create_app, db
from app.models.operation import Operation
from app.models.job import ProcessingJob
from app.models.fidc_cash import FidcCash
import json
from datetime import date

@pytest.fixture
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_process_operations(test_client, mocker):
    # Mock da task para não executar realmente
    mock_task = mocker.patch('app.api.routes.process_operations_batch_task.delay')

    # Dados para enviar
    data = {
        "fidc_id": "FIDC_TEST",
        "operations": [
            {
                "id": "op_001",
                "asset_code": "PETR4",
                "operation_type": "BUY",
                "quantity": 1000,
                "operation_date": "2025-09-01"
            }
        ]
    }

    # Enviar request
    response = test_client.post(
        '/operations/process',
        data=json.dumps(data),
        content_type='application/json'
    )

    # Verificar resposta
    assert response.status_code == 202
    response_data = json.loads(response.data)
    assert 'job_id' in response_data
    assert response_data['total_operations'] == 1

    # Verificar que task foi chamada
    mock_task.assert_called_once()

    # Verificar que dados foram salvos no banco
    with test_client.application.app_context():
        operation = Operation.query.first()
        assert operation is not None
        assert operation.id == "op_001"

        job = ProcessingJob.query.first()
        assert job is not None
        assert job.total_operations == 1

        # Verificar que FIDC foi criado automaticamente
        fidc = FidcCash.query.first()
        assert fidc is not None
        assert fidc.fidc_id == "FIDC_TEST"
        assert fidc.available_cash == 1_000_000.0

def test_job_status(test_client):
    # Criar job no banco
    with test_client.application.app_context():
        job = ProcessingJob(
            job_id="test-job-123",
            status="PROCESSING",
            total_operations=10,
            processed=5,
            failed=0
        )
        db.session.add(job)
        db.session.commit()

    # Consultar status
    response = test_client.get('/jobs/test-job-123/status')

    # Verificar resposta
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['job_id'] == "test-job-123"
    assert response_data['progress'] == 50.0

def test_export_operations(test_client, mocker):
    # Mock de export_operations
    mock_url = "http://localhost:9000/fidc-exports/FIDC_TEST/export.csv"
    mocker.patch('app.api.routes.export_operations', return_value=mock_url)

    # Dados para enviar
    data = {
        "fidc_id": "FIDC_TEST",
        "start_date": "2025-09-01",
        "end_date": "2025-09-30"
    }

    # Enviar request
    response = test_client.post(
        '/operations/export',
        data=json.dumps(data),
        content_type='application/json'
    )

    # Verificar resposta
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'download_url' in response_data
    assert response_data['download_url'] == mock_url
