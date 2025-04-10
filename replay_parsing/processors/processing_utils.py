from utils.helpers import is_invalid_value


def process_output(output, allow_none: bool = False):
    if is_invalid_value(output):
        return None if allow_none else 0

    if isinstance(output, float) or isinstance(output, int):
        return output

    return float(output)


def is_numeric_type(value, none_is_true: bool = True) -> bool:
    if none_is_true and value is None:
        return True

    if not (isinstance(value, float) or isinstance(value, int)):
        return False

    return True


def add_data_type_name(text: str, text_to_add: str) -> str:
    return f'{text_to_add}|{text}'
