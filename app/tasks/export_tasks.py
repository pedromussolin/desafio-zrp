from celery import shared_task
from app.services.export_service import ExportService

@shared_task
def export_operations_to_bucket(data):
    export_service = ExportService()
    result = export_service.export(data)
    return result