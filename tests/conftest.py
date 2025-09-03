import pytest
from app import create_app
from app.models import db

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "CELERY_TASK_ALWAYS_EAGER": True,
        "CELERY_BROKER_URL": "redis://localhost:6379/0",
        "CELERY_RESULT_BACKEND": "redis://localhost:6379/0"
    })
    with app.app_context():
        db.create_all()
        yield app

@pytest.fixture()
def client(app):
    return app.test_client()
