from decimal import Decimal
from typing import Any

def convert_floats_to_decimals(data: Any) -> Any:
    """
    Recursivey convert all float values to Decimal types for DynamoDB

    :param data: The data to convert
    :return: The data with float values converted to Decimal
    """
    
    if isinstance(data, dict):
        return {k: convert_floats_to_decimals(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_floats_to_decimals(item) for item in data]
    elif isinstance(data, float):
        return Decimal(str(data)) # Convert via string to avoid precision issues
    else:
        return data
    