import copy
from typing import Dict, List, Tuple

import pandas as pd

from utils import iterate_df


def _count_fk(fk_list: List[bool]) -> bool | None:
    if (sum_ := sum(fk_list) >= 10):
        return True
    if (len(fk_list) - sum_) >= 10:
        return False
    return None


def process_hero_deaths(df: pd.DataFrame, players_to_slot: Dict[str, int]) -> tuple[dict, bool | None, list]:
    df[['sourcename', 'targetname', ]] = df[['sourcename', 'targetname', ]].replace(players_to_slot)
    # 7483084944
    # TODO: KeyError: "None of [Index(['sourcename', 'targetname'], dtype='object')] are in the [columns]"

    player_data = {x: {
        'first_blood_claimed': False,
        'first_kill_time': None,

        'died_first': False,
        'first_death_time': None,
    } for x in range(10)}

    hero_death_base = {
        'death_number': None,
        'death_time': None,

        'kill_slot': None,
        'kill_dire': None,

        'victim_slot': None,
        'victim_dire': False,
    }

    hero_deaths = []
    first_ten_kills_dire = None

    fk_list = []
    for index, item in iterate_df(df):
        hero_death = copy.copy(hero_death_base)

        killer_slot = None
        kill_dire = None
        if isinstance(item['sourcename'], int):
            killer_slot = item['sourcename']
            kill_dire = True if killer_slot > 4 else False
            fk_list.append(kill_dire)

        victim_slot = item['targetname']
        time_time = item['time']

        # FIRST BLOOD
        if index == 1:
            if killer_slot is not None:
                player_data[killer_slot]['first_blood_claimed'] = True
                player_data[killer_slot]['first_kill_time'] = time_time

            player_data[victim_slot]['died_first'] = True
            player_data[victim_slot]['first_death_time'] = time_time

        # DEATH DATA
        hero_death['death_number'] = index
        hero_death['death_time'] = time_time

        hero_death['kill_slot'] = killer_slot
        hero_death['kill_dire'] = kill_dire

        hero_death['victim_slot'] = victim_slot
        hero_death['victim_dire'] = True if victim_slot > 4 else False

        if len(fk_list) > 10 and first_ten_kills_dire is None:
            first_ten_kills_dire = _count_fk(fk_list)

        hero_deaths.append(hero_death)

    return (player_data, first_ten_kills_dire, hero_deaths)


def process_roshan_deaths(df: pd.DataFrame, players_to_slot: Dict[str, int]) -> Tuple[float | int, list]:
    roshan_kill_base = {
        'death_number': None,
        'death_time': None,
        'kill_dire': None,
    }

    roshan_death = []
    average_roshan_window_time = 0

    if df.empty:
        return (average_roshan_window_time, roshan_death)

    df['sourcename'] = df['sourcename'].replace(players_to_slot)

    killing_time = []
    for index, item in iterate_df(df):
        roshan_kill = copy.deepcopy(roshan_kill_base)

        kill_dire = None
        if isinstance(item['sourcename'], int):
            kill_dire = True if item['sourcename'] > 4 else False

        roshan_kill['death_number'] = index
        roshan_kill['death_time'] = item['time']
        roshan_kill['kill_dire'] = kill_dire

        killing_time.append(item['time'])
        roshan_death.append(roshan_kill)

    if (kill_time_len := len(killing_time)):
        average_roshan_window_time = sum(killing_time) / kill_time_len

    return (average_roshan_window_time, roshan_death)
