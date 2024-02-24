import re
from decimal import Decimal
from typing import Generator, TypeVar, Type


SQLModelModel = TypeVar('SQLModelModel')


def _get_fields(model: SQLModelModel) -> Generator:
    schema = model.schema()

    fields, req_fields = schema['properties'], schema['required']

    for f_name, f_props in fields.items():
        is_required = True if f_name in req_fields else False

        is_comparable = True
        match f_props['type']:
            case 'integer':
                func_ = int
            case 'number':  # float
                func_ = float
            case 'boolean':
                func_ = bool
            case _:
                func_ = None
                is_comparable = False

        if not is_comparable or re.search(r'(^|_)id$', f_name):
            continue

        yield f_name, func_, f_props['type'], is_required


def compare_performance(comparandum_obj: SQLModelModel,
                        comparans_obj: SQLModelModel,
                        output_obj: Type[SQLModelModel],
                        percent: bool,
                        coef: int = 1,
                        ) -> SQLModelModel:
    output_dict = dict()

    for name, type_func, type_name, is_required in _get_fields(output_obj):

        comparandum_value = getattr(comparandum_obj, name)
        comparans_value = getattr(comparans_obj, name)

        if (comparandum_value is None or comparans_value is None) and not is_required:
            output_dict[name] = None
            continue

        if type_func is bool:
            output_dict[name] = (comparandum_value == comparans_value)
        else:
            if (not comparandum_value or not comparans_value) and percent:
                output_dict[name] = 0
                continue

            adjusted_cps_v = (comparans_value / coef)

            if percent:
                output_dict[name] = type_func(comparandum_value / adjusted_cps_v)
            else:
                output_dict[name] = type_func(comparandum_value - adjusted_cps_v)

            if type_name == 'number':
                output_dict[name] = round(Decimal(output_dict[name]))

    return output_obj(**output_dict)


def combine_total_performance(comparandum_obj: SQLModelModel,
                              comparans_obj: SQLModelModel,
                              output_obj: Type[SQLModelModel],
                              ) -> SQLModelModel:
    output_dict = dict()

    for name, type_func, type_name, is_required in _get_fields(output_obj):

        comparandum_value = getattr(comparandum_obj, name)
        comparans_value = getattr(comparans_obj, name)

        if (comparandum_value is None or comparans_value is None) and not is_required:
            output_dict[name] = None
            continue

        if type_func is bool:
            output_dict[name] = (comparandum_value == comparans_value)
        else:
            if (not comparandum_value or not comparans_value):
                output_dict[name] = 0
            elif not comparandum_value:
                output_dict[name] = comparans_value
            elif not comparans_value:
                output_dict[name] = comparandum_value
            else:
                output_dict[name] = type_func(comparandum_value + comparans_value)

            if type_name == 'number':
                output_dict[name] = round(Decimal(output_dict[name]))

    return output_obj(**output_dict)
