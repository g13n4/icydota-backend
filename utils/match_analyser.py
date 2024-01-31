import re
from decimal import Decimal
from typing import Tuple

from pydantic.fields import ModelField


def _comparable(mf: ModelField) -> Tuple[bool, bool]:
    """Check if value can be compared i.e. not a model, id key, string, etc
    :returns two booleans: first - can the value be compared, second - is it a boolean value
    """
    for func_ in [issubclass, isinstance]:
        if func_(mf.outer_type_, bool):
            return (True, True)

    # we need to separate them to ensure that a bool type is not just an int
    for func_ in [issubclass, isinstance]:
        if func_(mf.outer_type_, (int, float, Decimal,)):
            return (True, False)

    return (False, False)


def compare_performance(comparandum_obj, comparans_obj, output_obj, percent: bool):
    output_dict = {}
    for name, mf in output_obj.__fields__.items():
        if name in ['id'] or re.search(r'_id$', name):
            continue

        is_comparable, is_bool = _comparable(mf)

        comparandum_value = getattr(comparandum_obj, name)
        comparans_value = getattr(comparans_obj, name)

        if (not is_comparable) or comparandum_value is None or comparans_value is None:
            continue

        if is_bool:
            output_dict[name] = comparandum_value == comparans_value
        else:
            if percent:
                output_dict[name] = comparandum_value / comparans_value
            else:
                output_dict[name] = comparandum_value - comparans_value

    return output_obj(**output_dict)
