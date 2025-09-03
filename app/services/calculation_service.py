from app.models.operation import Operation

def calculate_operation_value(operation: Operation) -> float:
    if operation.operation_type == 'BUY':
        return operation.quantity * operation.execution_price
    elif operation.operation_type == 'SELL':
        return operation.quantity * operation.execution_price - operation.tax_paid
    else:
        raise ValueError("Invalid operation type")