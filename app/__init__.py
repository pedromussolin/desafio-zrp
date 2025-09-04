from flask import Flask
from .config import Config
from .models import db
from celery import Celery
import logging

# Importar modelos - DEPOIS da importação de db para evitar circular imports
from .models.operation import Operation
from .models.job import ProcessingJob
from .models.fidc_cash import FidcCash

celery = Celery(__name__)

def init_celery(app: Flask):
    """Initialize Celery with Flask app configuration"""
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        task_track_started=True
    )

    # Registrar tasks após config sem criar dependência circular
    # NÃO importamos tarefas aqui, em vez disso o worker as importa diretamente

def create_app(config_class=Config):
    """Create Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Logging simples estruturado
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Blueprints - Importar o blueprint diretamente sem importar routes
    from .api import api_bp
    app.register_blueprint(api_bp)

    init_celery(app)

    return app
