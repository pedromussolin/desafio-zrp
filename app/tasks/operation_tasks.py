from celery import Celery
from app import create_app, db
from app.models import Operation, Job
from app.services.calculation_service import calculate_operation
from app.services.job_service import create_job

app = create_app()
celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task(bind=True)
def process_operation(self, operation_data):
    job = create_job()
    try:
        operation = Operation(**operation_data)
        db.session.add(operation)
        db.session.commit()
        
        # Perform calculation
        result = calculate_operation(operation)
        
        # Update operation with result
        operation.execution_price = result['execution_price']
        operation.total_value = result['total_value']
        operation.tax_paid = result['tax_paid']
        operation.status = 'completed'
        
        db.session.commit()
        return {'status': 'success', 'operation_id': operation.id}
    except Exception as e:
        db.session.rollback()
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {'status': 'failure', 'error': str(e)}