from datetime import datetime, timezone
from app.models.job import Job
from app import db

class JobService:
    @staticmethod
    def create_job():
        job = Job(status='PENDING', created_at=datetime.now(timezone.utc))
        db.session.add(job)
        db.session.commit()
        return job

    @staticmethod
    def get_job_status(job_id):
        job = Job.query.get(job_id)
        if job:
            return {
                'job_id': job.job_id,
                'status': job.status,
                'created_at': job.created_at,
                'completed_at': job.completed_at
            }
        return None

    @staticmethod
    def update_job_status(job_id, status):
        job = Job.query.get(job_id)
        if job:
            job.status = status
            if status == 'COMPLETED':
                job.completed_at = datetime.now(timezone.utc)
            db.session.commit()
            return job
        return None

    @staticmethod
    def get_all_jobs():
        return Job.query.all()
