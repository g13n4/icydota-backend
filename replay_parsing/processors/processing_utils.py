from typing import Callable
import numpy as np


def process_output(output, allow_none: bool = False):
    if output is None or output is np.inf or output is np.nan:
        return None if allow_none else 0

    if isinstance(output, float) or isinstance(output, int):
        return output

    return float(output)


def normalise_output_type_wrapper(allow_none: bool = False):
    def wrapper_outer(func: Callable) -> Callable:
        def wrapper_inner(*args, **kwargs) -> int | float | None:
            output = func(*args, **kwargs)

            return process_output(output, allow_none=allow_none)
        return wrapper_inner
    return wrapper_outer


def is_numeric_type(value, none_is_true: bool = True) -> bool:
    if none_is_true and value is None:
        return True

    if not (isinstance(value, float) or isinstance(value, int)):
        return False

    return True


def add_data_type_name(text: str, text_to_add: str) -> str:
    return f'{text_to_add}|{text}'
