from decimal import Decimal


def decimal_division(a: Decimal | int | float, b: Decimal | int | float, bool_normalize: bool = False):
    if not a or not b:
        value = None
    else:
        if not isinstance(a, Decimal):
            a = Decimal(a)

        if not isinstance(b, Decimal):
            b = Decimal(b)

        value = a / b

    if bool_normalize:
        if value is None:
            value = 0.0
        else:
            value = min(max(value, 0), 1)

    return value if value is None else Decimal(value)
