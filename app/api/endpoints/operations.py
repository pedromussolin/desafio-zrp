from flask import Blueprint, request, jsonify
from app.models.operation import Operation
from app.services.calculation_service import calculate_operation
from app.services.job_service import create_job
from app.tasks.operation_tasks import process_operation_task

operations_bp = Blueprint('operations', __name__)

@operations_bp.route('/operations/process', methods=['POST'])
def process_operations():
    data = request.json
    asset_code = data.get('asset_code')
    operation_type = data.get('operation_type')
    quantity = data.get('quantity')

    if not all([asset_code, operation_type, quantity]):
        return jsonify({'error': 'Missing required fields'}), 400

    total_value, execution_price, tax_paid = calculate_operation(asset_code, operation_type, quantity)

    operation = Operation(
        asset_code=asset_code,
        operation_type=operation_type,
        quantity=quantity,
        execution_price=execution_price,
        total_value=total_value,
        tax_paid=tax_paid
    )
    
    job_id = create_job(operation)

    process_operation_task.delay(job_id)

    return jsonify({'job_id': job_id}), 202