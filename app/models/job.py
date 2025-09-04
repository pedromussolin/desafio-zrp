from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from app.models import db

class Job(db.Model):
    __tablename__ = 'jobs'

    job_id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f'<Job {self.job_id} - Status: {self.status}>'

class ProcessingJob(db.Model):
    __tablename__ = "processing_jobs"

    job_id = db.Column(db.String(36), primary_key=True)
    status = db.Column(db.String(20), default="PROCESSING")  # PROCESSING|COMPLETED|FAILED
    total_operations = db.Column(db.Integer, default=0)
    processed = db.Column(db.Integer, default=0)
    failed = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    estimated_completion = db.Column(db.DateTime, nullable=True)
