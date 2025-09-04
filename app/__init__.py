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
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        task_track_started=True
    )
    # Registrar tasks após config
    from .tasks import operation_tasks  # noqa

def create_app(config_class=Config):
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

    # Blueprints
    from .api.routes import api_bp
    app.register_blueprint(api_bp)

    init_celery(app)

    return app
