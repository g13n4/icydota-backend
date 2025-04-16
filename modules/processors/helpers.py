from decimal import Decimal


def decimal_division(a: Decimal | int | float, b: Decimal | int | float, bool_normalize: bool = False):
    if not a or not b:
        value = None
    else:
        value = a / b

    if bool_normalize:
        if value is None:
            value = 0.0
        else:
            value = min(max(value, 0), 100)

    return value if value is None else Decimal(value)
