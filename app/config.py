import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # Banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://fidc:fidc@db:5432/fidc')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
    CELERY_TASK_TIME_LIMIT = 60 * 5
    CELERY_TASK_SOFT_TIME_LIMIT = 60 * 4
    CELERY_TASK_TRACK_STARTED = True

    PRICE_API_FAILURE_RATE = float(os.getenv("PRICE_API_FAILURE_RATE", "0.3"))
    PRICE_API_RATE_LIMIT_PER_MINUTE = int(os.getenv("PRICE_API_RATE_LIMIT_PER_MINUTE", "10"))

    # MinIO
    MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'minio:9000')
    MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
    MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'minioadmin')
    MINIO_BUCKET = os.environ.get('MINIO_BUCKET', 'fidc-exports')

    JOB_ESTIMATION_WINDOW = timedelta(seconds=5)
