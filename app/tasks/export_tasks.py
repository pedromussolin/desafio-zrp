from celery import shared_task
from app.services.export_service import export_operations

@shared_task
def export_operations_task(fidc_id, start_date, end_date):
    """
    Export operations from a date range to a CSV file in MinIO
    """
    result = export_operations(fidc_id, start_date, end_date)
    return result
