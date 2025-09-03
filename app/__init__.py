from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
import os

db = SQLAlchemy()

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    return celery

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    celery = make_celery(app)

    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    return app, celery

app, celery = create_app()