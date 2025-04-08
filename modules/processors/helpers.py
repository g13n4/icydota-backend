from decimal import Decimal


def decimal_division(a: Decimal | int | float, b: Decimal | int | float):
    if not a or not b:
        return None
    return a / b
