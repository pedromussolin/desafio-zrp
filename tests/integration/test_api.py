from app import create_app
import pytest

app = create_app()

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_process_operations(client):
    response = client.post('/operations/process', json={
        'asset_code': 'BTC',
        'operation_type': 'BUY',
        'quantity': 1.5
    })
    assert response.status_code == 202
    assert 'job_id' in response.json

def test_check_job_status(client):
    response = client.get('/jobs/1/status')
    assert response.status_code == 200
    assert 'status' in response.json

def test_export_operations(client):
    response = client.post('/operations/export', json={
        'operation_ids': [1, 2, 3]
    })
    assert response.status_code == 202
    assert 'job_id' in response.json

def test_invalid_process_operations(client):
    response = client.post('/operations/process', json={
        'asset_code': 'INVALID',
        'operation_type': 'BUY',
        'quantity': -1
    })
    assert response.status_code == 400
    assert 'error' in response.json

def test_invalid_export_operations(client):
    response = client.post('/operations/export', json={
        'operation_ids': []
    })
    assert response.status_code == 400
    assert 'error' in response.json