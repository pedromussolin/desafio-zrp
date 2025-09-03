from celery import Celery
from flask import Flask
import os

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    return celery

app = Flask(__name__)
app.config.from_object('app.config.Config')

celery = make_celery(app)

if __name__ == '__main__':
    app.run()
