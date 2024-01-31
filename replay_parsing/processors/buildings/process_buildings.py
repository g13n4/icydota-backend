import copy
import re
from typing import List

import pandas as pd


def _detect_tier(value) -> int:
    for x in range(1, 5):
        if re.search(f'tower{x}', value):
            return x
    return 0


def _detect_lane(value) -> int:
    # 1 - bottom / 2 - mid / 3 - top
    if re.search('_bot', value):
        return 1
    elif re.search('_mid', value):
        return 2
    elif re.search('_top', value):
        return 3
    return 0


lane_to_pos = {
    1: {
        'sentinel': [1, 5], 'dire': [3, 4],
    },
    2: {
        'sentinel': [2], 'dire': [2],
    },
    3: {
        'sentinel': [3, 4], 'dire': [1, 5],
    },
}

lane_names = {
    0: '',  # 4 tier / throne
    1: 'bot',
    2: 'mid',
    3: 'top',
}


def _detect_rax(value) -> int:
    for idx, x in enumerate(['melee_rax', 'range_rax', ], 1):
        if re.search(x, value):
            return idx
    return 0


rax_names = {
    1: 'melee_rax',
    2: 'range_rax',
}

left_towers_to_vars = {
    (1, 3): 'towers_left_top',
    (1, 2): 'towers_left_mid',
    (1, 1): 'towers_left_bottom',
    (1, 0): 'towers_left_throne',

    1: 'towers_left_total',

    (0, 3): 'rax_left_top',
    (0, 2): 'rax_left_mid',
    (0, 1): 'rax_left_bottom',

    0: 'rax_left_total',
}


def _find_left_towers(killed_buildings: List[dict]) -> dict:
    left_towers = {
        (1, 3): 3,  # towers_left_top
        (1, 2): 3,  # towers_left_mid
        (1, 1): 3,  # towers_left_bottom
        (1, 0): 2,  # towers_left_throne

        1: 11,  # towers_left_total

        (0, 3): 2,  # rax_left_top
        (0, 2): 2,  # rax_left_mid
        (0, 1): 2,  # rax_left_bottom

        0: 6,  # rax_left_total
    }

    for building in killed_buildings:
        is_tower = building['is_tower']
        lane = building['lane']['value']
        left_towers[(is_tower, lane)] -= 1
        left_towers[is_tower] -= 1

    return {left_towers_to_vars[k]: v for k, v in left_towers.items()}


def _find_destroyed_lane(killed_buildings: List[dict]) -> None:
    lane_state = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
    }

    lane_destruction_status = {
        1: False,
        2: False,
        3: False,
    }

    tower_counter = 0
    rax_counter = 0
    throne_towers = 0

    killed_buildings.sort(key=lambda x: x['time'])
    for idx, item in enumerate(killed_buildings, 1):
        item['destruction_order'] = idx
        if item['is_tower']:
            tower_counter += 1
            item['tower']['destruction_order'] = tower_counter

            if item['tower']['tier'] == 4:
                throne_towers += 1
                item['lane']['tower4'] = False
                if throne_towers == 2:
                    item['naked_throne'] = True
                    item['lane']['tower4'] = True
        else:
            rax_counter += 1
            item['rax']['destruction_order'] = rax_counter

            lane_state[item['lane']['value']] += 1

            lsv = lane_state[item['lane']['value']]
            if lsv == 2:
                item['lane']['destroyed_lane'] = True
                lane_destruction_status[item['lane']['value']] = True

                lane_state[4] += 1

                if lane_state[4] == 3:
                    item['megacreeps'] = True

        item['lanes_destroyed'] = copy.deepcopy(lane_destruction_status)


def process_building_kill_df(df: pd.DataFrame) -> pd.DataFrame:
    df_contains = df['targetname'].str.contains
    df = df[(df.value > 0) & (df.value < 3)].copy()
    df['dire'] = df_contains('npc_dota_badguys', regex=True)

    df['tier'] = df['targetname'].apply(_detect_tier)
    df['lane'] = df['targetname'].apply(_detect_lane)
    df['rax'] = df['targetname'].apply(_detect_rax)

    return df


def process_building(df: pd.DataFrame, pos_to_slot: dict) -> (dict, bool, dict):
    new_df = process_building_kill_df(df)
    # TODO: check 7254189995 KeyError: 'targetname'

    position_towers_status = {x: {
        'lost_tower_first': False,
        'lost_tower_lane': None,
        'lost_tower_time': None,

        'destroyed_tower_first': False,
        'destroyed_tower_lane': None,
        'destroyed_tower_time': None,
    } for x in range(10)}

    dire_t_died = []
    sent_t_died = []

    dire_lost_first_tower = None
    first_tower = True
    for idx, v in new_df[['time', 'dire', 'tier', 'lane', 'rax']].iterrows():
        values = v.to_dict()

        building = {
            'time': values['time'],
            'tower': {
                'tier': values['tier'],
                'destruction_order': None,  # for tower
            },
            'is_tower': False if values['rax'] > 0 else True,
            'lane': {
                'tower4': None,
                'value': values['lane'],
                'name': lane_names[values['lane']],
                'destroyed_lane': False,
            },
            'dire': values['dire'],
            'rax': {
                'value': values['rax'],
                'name': lane_names[values['rax']],
                'destruction_order': None,  # for rax
            },  # lanes_destroyed is added later
            'destruction_order': None,
            'megacreeps': False,
            'naked_throne': False,
        }

        if values['dire']:  # dire tower died => it was killed by sentinels
            dire_t_died.append(building)
        else:
            sent_t_died.append(building)

        if first_tower:
            dire_lost_first_tower = values['dire']
            lost_t, killed_t = ('dire', 'sentinel') if dire_lost_first_tower else ('sentinel', 'dire')
            lost_t_pos = lane_to_pos[values['lane']][lost_t]
            killed_t_pos = lane_to_pos[values['lane']][killed_t]
            for pos in lost_t_pos:
                slot = pos_to_slot[lost_t][pos]

                position_towers_status[slot]['lost_tower_first'] = True
                position_towers_status[slot]['lost_tower_lane'] = values['lane']
                position_towers_status[slot]['lost_tower_time'] = values['time']

            for pos in killed_t_pos:
                slot = pos_to_slot[killed_t][pos]

                position_towers_status[slot]['destroyed_tower_first'] = True
                position_towers_status[slot]['destroyed_tower_lane'] = values['lane']
                position_towers_status[slot]['destroyed_tower_time'] = values['time']

            first_tower = False

    _find_destroyed_lane(dire_t_died)
    _find_destroyed_lane(sent_t_died)

    dire_left = _find_left_towers(dire_t_died)
    sentinel_left = _find_left_towers(sent_t_died)

    return (position_towers_status,
            dire_lost_first_tower,
            {
                'dire_died': dire_t_died,
                'sentinel_died': sent_t_died,

                'dire_left': dire_left,
                'sentinel_left': sentinel_left, })
