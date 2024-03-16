import re
from typing import List, Optional, Dict


COLUMNS_DICT = {
    'l2': '-1.5m - 2m',
    'l4': '2m - 4m',
    'l6': '4m - 6m',
    'l8': '6m - 8m',
    'l10': '8m - 10m',
    'ltotal': '<10m',

    # next phase
    'g15': '-1.5m - 15m',
    'g30': '15m - 30m',
    'g45': '30m - 45m',
    'g60': '45m - 60m',
    'g60plus': '60m - the game\'s end',
    'gtotal': 'by the game\'s end',

    # names
    'player_id': 'player id',
    'player_name': 'nickname',

    'position_id': 'position',
    'opponents_pos': 'opponents position',

    'hero_id': 'hero id',
    'hero_name': 'hero',

    # game stage
    'l_data': 'Early game',
    'g_data': 'Late game',

    'game_stage': 'Game stage',
}


def to_proper_name(value: str, split: str = '_') -> str:
    return ' '.join(value.split(split)).capitalize()


def get_field_name(value: str, sum_total: Optional[bool] = None):
    if value.endswith('total'):
        field_name = COLUMNS_DICT[value]
        if sum_total is None:
            field_name += ' (not calculated)'
        elif sum_total:
            field_name += ' (SUM)'
        else:
            field_name += ' (AVG)'

        return field_name

    if value in COLUMNS_DICT:
        return COLUMNS_DICT[value]

    return to_proper_name(value)



def _key_sort_func(name: str) -> int:
    # WINDOWS
    if (re_match := re.match(r'^[l|g]((\d+)|total)(plus)?', name)):
        if re_match[1] == 'total':
            return 100
        if 'plus' in re_match[1]:
            return 90
        else:
            return int(re_match[1])
    else:
        # TOTALS
        if 'gold' in name:
            return 0
        if 'xp' in name:
            return 1
        if 'hero_kills' in name:
            return 2
        if 'kda' in name:
            return 3
        if 'kills_per_minute' in name:
            return 4
        if 'lane_kills' in name:
            return 5
        if 'neutral_kills' in name:
            return 6
        if 'ancient_kills' in name:
            return 7
        if 'tower_kills' in name:
            return 8
        if 'roshan_kills' in name:
            return 9
        if 'courier_kills' in name:
            return 10
        if 'observer_uses' in name:
            return 11
        if 'sentry_uses' in name:
            return 12
        if 'runes_picked_up' in name:
            return 13
        if 'buyback_count' in name:
            return 14

        score = 0
        if 'lane_efficiency' in name:
            score += 100
        if re.match(r'first_(blood|kill)', name):
            score += 200
        if re.match('(died_first)|(first_death)', name):
            score += 300
        if 'lost_tower' in name:
            score += 400
        if 'destroyed_tower' in name:
            score += 500
        if 'lane' in name:
            score += 15
        if 'time' in name:
            score += 10

        return score


def to_table_format(data: List[dict], data_info: List[dict],  rows: list, sum_total: Optional[bool] = None) -> dict:
    if not data:
        return {}

    item = data[0]

    values = sorted([key_name for key_name in item.keys() if key_name not in rows], key=_key_sort_func)

    fields = {'rows': rows,
              'columns': [],
              'values': values,
              'valueInCols': True, }

    meta = [{
        'field': x,
        'name': get_field_name(x, sum_total), } for x in item.keys()]

    return {
        "table_data": {
            'fields': fields,
            'meta': meta,
            'data': data,
        },
        "table_options": {
            "style": {
                "layoutWidthType": 'colAdaptive', },
        },
        "table_values": data_info,
    }


def to_table_format_cross_comparison(data: Dict[int, list],
                                     values_info: list,
                                     aggregation_type: str) -> dict:
    if not data:
        return {}


    fields = {'rows': [aggregation_type],  # hero/pos/player | l2/g2/etc
              'columns': [],
              'values': sorted(data.keys()),  # classic windows/ total_values
              'valueInCols': True, }

    return {
        "table_data": {
            'fields': fields,
            'data': [x for x in data.values()],
        },
        "table_options": {
            "style": {
                "layoutWidthType": 'colAdaptive', },
            'interaction': {
            'hoverHighlight': 'true',
            }
        },
        "table_values": values_info,
    }
