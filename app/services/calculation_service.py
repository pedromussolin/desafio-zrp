from app.models.operation import Operation

def calculate_operation(price, quantity, operation_type):
    """
    Calculate total value and tax for an operation.

    Args:
        price (float): Asset price
        quantity (int): Number of assets
        operation_type (str): BUY or SELL

    Returns:
        tuple: (total_value, tax_paid)
    """
    total_value = price * quantity

    # Simular um cálculo de taxa simples (0.2% para compra, 0.3% para venda)
    tax_rate = 0.002 if operation_type == "BUY" else 0.003
    tax_paid = total_value * tax_rate

    return total_value, tax_paid
