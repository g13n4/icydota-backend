import re
from typing import Dict, Any, List
from utils import get_sqlmodel_fields


COLUMNS_DICT = {
    'l2': '-1.5m - 2m',
    'l4': '2m - 4m',
    'l6': '4m - 6m',
    'l8': '6m - 8m',
    'l10': '8m - 10m',
    'ltotal': '<10m (total)',

    # next phase
    'g15': '-1.5m - 15m',
    'g30': '15m - 30m',
    'g45': '30m - 45m',
    'g60': '45m - 60m',
    'g60plus': '60m - the game\'s end',
    'gtotal': 'by the game\'s end (total)',

    # names
    'player_id': 'player id',
    'player_name': 'nickname',

    'position_id': 'position',

    'hero_id': 'hero id',
    'hero_name': 'hero',

    # game stage
    'l_data': 'Early game',
    'g_data': 'Late game',

    'game_stage': 'Game stage',
}


def to_proper_name(value: str, split: str = '_') -> str:
    return ' '.join(value.split(split)).capitalize()


def to_table_format(data: List[dict], rows: list, ) -> dict:
    if not data:
        return {}

    item = data[0]

    values = [key_name for key_name in item.keys() if key_name not in rows]

    fields = {'rows': rows,
              'columns': [],
              'values': values,
              'valueInCols': True, }

    meta = [{
        'field': x,
        'name': COLUMNS_DICT.get(x, to_proper_name(x)), } for x in item.keys()]

    return {
        'fields': fields,
        'meta': meta,
        'data': data, }


def get_table_data_match_windows(output_model, data: list, use_ids: bool = False) -> dict:
    model_fields = get_sqlmodel_fields(output_model, include_ids=True)

    if use_ids:
        rows = ['player_id']
        additional_values = ['hero_id', 'position_id']
    else:
        rows = ['player_name']
        additional_values = ['hero_name', 'position_id']

    columns = []

    values = [x for x in model_fields if x not in ['data_type_id']]

    fields = {'rows': rows,
              'columns': columns,
              'values': additional_values + values,
              'valueInCols': True, }

    meta = [{
        'field': x,
        'name': COLUMNS_DICT[x], } for x in values + columns + rows + additional_values]

    data = [{**item.dict(include=set(model_fields + additional_values + rows)), } for item in data]

    return {
        'fields': fields,
        'meta': meta,
        'data': data, }


def get_table_data_match_windows_slow(output_model, data: list, use_ids: bool = False) -> dict:
    model_fields = get_sqlmodel_fields(output_model, include_ids=True)

    if use_ids:
        rows = ['player_id']
        additional_values = ['hero_id', 'position_id']
    else:
        rows = ['player_name']
        additional_values = ['hero_name', 'position_id']

    columns = []

    values = [x for x in model_fields if x not in ['data_type_id']]

    fields = {'rows': rows,
              'columns': columns,
              'values': additional_values + values,
              'valueInCols': True, }

    meta = [{
        'field': x,
        'name': COLUMNS_DICT[x], } for x in values + columns + rows + additional_values]

    return {
        'fields': fields,
        'meta': meta,
        'data': data, }
