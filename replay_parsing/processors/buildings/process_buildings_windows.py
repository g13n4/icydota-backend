import copy
import re
import pandas as pd
from typing import Dict, List


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


def process_building_kill_df(df: pd.DataFrame) -> pd.DataFrame:
    df_contains = df['targetname'].str.contains
    df = df[(df.value > 0) & (df.value < 3)].copy()
    df['dire'] = df_contains('npc_dota_badguys', regex=True)

    df['tier'] = df['targetname'].apply(_detect_tier)
    df['lane'] = df['targetname'].apply(_detect_lane)
    df['rax'] = df['targetname'].apply(_detect_rax)

    return df


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

    tower_counter, rax_counter, throne_towers = 0, 0, 0

    killed_buildings.sort(key=lambda x: x['time'])
    for idx, item in enumerate(killed_buildings, 1):
        item['destruction_order'] = idx
        if item['is_tower']:
            tower_counter += 1
            item['tower']['destruction_order'] = tower_counter

            if item['tower']['tier'] == 4:
                throne_towers += 1
                if throne_towers == 2:
                    item['naked_throne'] = True
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


def process_building_windows(df: pd.DataFrame) -> dict:
    new_df = process_building_kill_df(df)
    dire_killed = []
    sent_killed = []
    for idx, v in process_building_kill_df(new_df)[['time', 'dire', 'tier', 'lane', 'rax']].iterrows():
        values = v.to_dict()

        building = {
            'time': values['time'],
            'tower': {
                'tier': values['tier'],
                'destruction_order': None,  # for tower
            },
            'is_tower': False if values['rax'] > 0 else True,
            'lane': {
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
            sent_killed.append(building)
        else:
            dire_killed.append(building)

    _find_destroyed_lane(sent_killed)
    _find_destroyed_lane(dire_killed)

    return {
        'dire_killed': dire_killed,
        'sent_killed': sent_killed,
    }
