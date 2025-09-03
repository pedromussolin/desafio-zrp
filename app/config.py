import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///fidc_api.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
    CELERY_TASK_TIME_LIMIT = 60 * 5
    CELERY_TASK_SOFT_TIME_LIMIT = 60 * 4
    CELERY_TASK_TRACK_STARTED = True

    PRICE_API_FAILURE_RATE = float(os.getenv("PRICE_API_FAILURE_RATE", "0.3"))
    PRICE_API_RATE_LIMIT_PER_MINUTE = int(os.getenv("PRICE_API_RATE_LIMIT_PER_MINUTE", "10"))

    # Export / S3 (MinIO)
    S3_ENDPOINT = os.getenv("S3_ENDPOINT", "localhost:9000")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
    S3_BUCKET = os.getenv("S3_BUCKET", "fidc-exports")
    S3_SECURE = os.getenv("S3_SECURE", "False").lower() == "true"

    JOB_ESTIMATION_WINDOW = timedelta(seconds=5)
