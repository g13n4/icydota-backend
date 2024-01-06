import re
from decimal import Decimal


def compare_total_performance(comparandum_obj, comparans_obj, output_obj):
    output_dict = {}
    for name, mf in output_obj.__fields__.keys():
        if name in ['id'] or re.search(r'_id$', name):
            continue

        if isinstance(mf.outer_type_, int) or issubclass(mf.outer_type_, Decimal):
            comparandum_value = getattr(comparandum_obj, name)
            comparans_value = getattr(comparans_obj, name)

            if not (comparandum_value and comparans_value):
                continue

            output_dict[name] = comparandum_value / comparans_value

    return output_obj(**output_dict)
