from decimal import Decimal
from functools import lru_cache
from random import getrandbits
from typing import Tuple

from constants.api import PoTEnum
from constants.performance.total.category import GameTotalsCategory
from constants.performance.total.total import FIELD_AVAILABILITY_DATA_REPRESENTATION_TYPE_LITERAL, GameTotals
from constants.performance.window import WINDOWS_BY_TYPE, WindowType, AllWindows
from models.performance import PerformanceWindowData, PerformanceWindowTable
from modules.empty_mask_converter import EmptyMaskConverter
from modules.minmax_finder import TableMinMaxFinder
from utils import is_na_decimal


@lru_cache(maxsize=12)
def get_total_required_fields(
        data_representation: FIELD_AVAILABILITY_DATA_REPRESENTATION_TYPE_LITERAL,
        pot: PoTEnum,
        is_comparison: bool = False,

):
    return list(
        GameTotals.VALUES(
            available_for=[data_representation, pot.value],
            only_field="name",
            only_comparable=is_comparison
        )
    )


def get_windows_required_fields(
        game_stage: str,
):
    return WINDOWS_BY_TYPE[game_stage].VALUES_NAMES


def set_calculated_data(TMMF: TableMinMaxFinder, calculated_data: dict) -> dict:
    output = dict()
    for field_name, value in calculated_data.items():
        if is_na_decimal(value):
            value = None

        output[field_name] = value

        # LOOKING FOR MIN AND MAX VALUES
        TMMF.add(column=field_name, value=value)

    return output


def extract_window_data(
        PWD_obj: PerformanceWindowData,
        PWT_obj: PerformanceWindowTable | None,
        game_stage: str,
) -> dict:
    output = dict()
    if PWT_obj is not None:
        output = PWT_obj.model_dump(include=WINDOWS_BY_TYPE[game_stage].VALUES_NAMES)

    for stage in WindowType.VALUES:
        windows_class = WINDOWS_BY_TYPE[game_stage]
        mask_value = getattr(PWD_obj, windows_class.empty_mask)
        if game_stage in ['both', stage] and mask_value is not None:
            mask_data = EmptyMaskConverter.mask_to_dict(mask_value, windows_class.VALUES_NAMES)
            output.update(mask_data)
    return output


def extract_window_data_for_field(
        PWD_obj: PerformanceWindowData,
        value: Decimal | None,
        field: str | None = None,
) -> Decimal | None:
    if value is not None:
        return value

    window_field_item = getattr(AllWindows, field)
    mask_value = getattr(PWD_obj, window_field_item.empty_mask)
    windows_class = WINDOWS_BY_TYPE[window_field_item.window_type]
    mask_data = EmptyMaskConverter.mask_to_dict(mask_value, windows_class.VALUES_NAMES)
    return mask_data.get(field, None)


def process_db_output(
        query,
        model_names: list[str],
        pot: PoTEnum,
        req_type: str,
        data_model_name: str,
        game_stage: str | None = None,
        is_comparison: bool | None = None,
) -> Tuple[list, dict, bool]:
    TMMF = TableMinMaxFinder()
    output = []

    for row in query:
        row_data = { name: data for name, data in zip(model_names, row) }
        if "side" in row_data:
            row_data['side'] = 'Dire' if row_data['side'] else 'Sentinel'

        if data_model_name == 'window_data':
            window_data = extract_window_data(row_data['window_data'], row_data['window_table'], game_stage)
            calculated_data = set_calculated_data(TMMF=TMMF, calculated_data=window_data)

            del row_data['window_data']
            del row_data['window_table']

        elif data_model_name == 'total_data':
            fields = get_total_required_fields(data_representation=req_type, pot=pot, is_comparison=is_comparison)
            calculated_data = set_calculated_data(
                TMMF=TMMF,
                calculated_data=row_data['total_data'].model_dump(include=fields)
            )

            del row_data['total_data']

        else:
            raise Exception("No data to process")

        row_data.update(calculated_data)
        output.append(row_data)

    return output, TMMF.get_minmax_values(), TMMF.has_totals()


def get_column_with_children(col_name: str) -> dict:
    return {
        "headerName": col_name,
        "wrapHeaderText": True,
        "autoHeaderHeight": True,
        "children": [],
    }


def extract_formatted_columns(
        data: list,
        pinned_columns: list[str],
        item_map: dict,
        is_total: bool,
) -> list[dict]:
    first_item = next(iter(data))
    header_columns = []
    data_columns = []
    salt = getrandbits(19)

    total_category_list = [
                              get_column_with_children("Details")
                          ] + [
                              get_column_with_children(item.description) for item in GameTotalsCategory.VALUES
                          ]

    for name in first_item.keys():
        this_item = item_map.get(name, None)
        this_dict = dict()
        this_dict["field"] = name
        this_dict["headerName"] = this_item and this_item.description or name.capitalize()

        if name in pinned_columns:
            this_dict["pinned"] = "left"

        if this_item is not None:
            this_dict["colId"] = f"{this_item.index}-{salt}"
            this_dict["orderId"] = f"{this_item.index}"
            if is_total:
                category_index = this_item.category.value
                total_category_list[category_index]["children"].append(this_dict)
            else:
                data_columns.append(this_dict)
        else:
            this_dict["colId"] = f"{name}-{salt}"
            this_dict["orderId"] = f"{name}"
            if is_total:
                total_category_list[0]["children"].append(this_dict)
            else:
                header_columns.append(this_dict)

    if is_total:
        [children["children"].sort(key=lambda x: x["orderId"]) for children in total_category_list]
        return total_category_list

    else:
        data_columns.sort(key=lambda x: x["orderId"])
        return header_columns + [item for item in data_columns]


def format_formatted_columns(pinned_column: str, columns: list[str]) -> list[dict]:
    output = list()
    salt = getrandbits(19)
    output.append(
        {
            "field": pinned_column,
            "headerName": pinned_column,
            "pinned": "left",

        }
    )
    for name in columns:
        this_dict = dict()
        this_dict["field"] = name
        this_dict["headerName"] = name
        this_dict["colId"] = f"{name}-{salt}"

        output.append(this_dict)
    return output
