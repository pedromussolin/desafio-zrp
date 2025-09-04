from datetime import datetime, timezone
from app.models.job import Job, ProcessingJob
from app import db
import logging

logger = logging.getLogger(__name__)

class JobService:
    @staticmethod
    def create_job():
        job = Job(status='PENDING', created_at=datetime.now(timezone.utc))
        db.session.add(job)
        db.session.commit()
        return job

    @staticmethod
    def get_job_status(job_id):
        """
        Get job status and statistics

        Args:
            job_id (str): Job ID

        Returns:
            dict: Job status information
        """
        job = ProcessingJob.query.get(job_id)
        if not job:
            return None

        result = {
            "job_id": job.job_id,
            "status": job.status,
            "total_operations": job.total_operations,
            "processed": job.processed,
            "failed": job.failed,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }

        # Calculate progress percentage
        if job.total_operations > 0:
            result["progress"] = round((job.processed + job.failed) / job.total_operations * 100, 1)
        else:
            result["progress"] = 0

        return result

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

# Helpers para compatibilidade com código antigo
def create_job():
    """Helper function that calls JobService.create_job()"""
    return JobService.create_job()

def get_job_status(job_id):
    """Helper function that calls JobService.get_job_status()"""
    return JobService.get_job_status(job_id)
