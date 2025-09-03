def calculate_total_value(quantity, execution_price):
    return quantity * execution_price

def format_response(data, message=None):
    response = {
        "data": data,
        "message": message
    }
    return response

def validate_operation_data(data):
    required_fields = ['asset_code', 'operation_type', 'quantity', 'execution_price']
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    return True, "Validation successful"

def log_operation(operation):
    # Placeholder for logging logic
    print(f"Operation logged: {operation}")