from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app import db

class Job(db.Model):
    __tablename__ = 'jobs'

    job_id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f'<Job {self.job_id} - Status: {self.status}>'