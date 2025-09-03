from celery import Celery
from flask import Flask
import os
from app import create_app, celery

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    return celery

app = Flask(__name__)
app.config.from_object('app.config.Config')

celery = make_celery(app)

flask_app = create_app()

# Permite tasks usarem app context
class AppContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)

celery.Task = AppContextTask

if __name__ == '__main__':
    flask_app.run()
