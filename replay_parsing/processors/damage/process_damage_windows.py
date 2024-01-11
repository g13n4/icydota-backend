from functools import partial
from typing import List, Tuple

import numpy as np
import pandas as pd

from replay_parsing.modules import MatchSplitter
from utils import create_player_windows
from ..aggregations import WINDOWS_BASE_NULLS
from ..processing_utils import add_data_type_name
from ..processing_utils import process_output
from ...windows import DAMAGE_WINDOWS

PROCESSED_DATA_NAME = 'damage'
AN = partial(add_data_type_name, text_to_add=PROCESSED_DATA_NAME)
PO = partial(process_output, allow_none=False)


def _concat_to_slot(slot: int):
    def _concat(text: str) -> str:
        return '|'.join([f'{slot}', text])

    return _concat

def _split_damage_by_player(df: pd.DataFrame, players: list) -> pd.DataFrame:
    df['frombuilding'] = df['sourcename'].str.contains('_tower|_rax_|_fillers|fort', regex=True)
    df['tobuilding'] = df['targetname'].str.contains('_tower|_rax_|_fillers|fort', regex=True)

    ser_with_summons = df.attackerhero != True
    ser_to_heroes = df.targethero == True
    ser_to_buildings = df.tobuilding == True
    ser_to_creatures = ((df.tobuilding == False) &
                        (df.targethero == False) &
                        (df.targetillusion == False))
    ser_to_illusions = df.targetillusion == True

    ser_from_heroes = df.attackerhero == True
    ser_from_buildings = df.frombuilding == True
    ser_from_creatures = ((df.frombuilding == False) &
                          (df.attackerhero == False) &
                          (df.attackerillusion == False))
    ser_from_illusions = df.attackerillusion == True

    new_columns = {}
    for player in players:
        name_match = player['hero_npc_name'] + \
                     (f"|{player['hero_npc_name_alias']}" if player['hero_npc_name_alias'] else '')
        player_attack = df['sourcename'].str.contains(name_match, regex=True)
        player_defense = df['targetsourcename'].str.contains(name_match, regex=True)

        concat_ = _concat_to_slot(player['slot'])

        new_columns[concat_('with_summons')] = player_attack & ser_with_summons
        new_columns[concat_('to_heroes')] = player_attack & ser_to_heroes

        new_columns[concat_('to_buildings')] = player_attack & ser_to_buildings
        new_columns[concat_('to_creatures')] = player_attack & ser_to_creatures
        new_columns[concat_('to_illusions')] = player_attack & ser_to_illusions
        new_columns[concat_('to_all')] = player_attack

        new_columns[concat_('from_heroes')] = player_defense & ser_from_heroes
        new_columns[concat_('from_buildings')] = player_defense & ser_from_buildings
        new_columns[concat_('from_creatures')] = player_defense & ser_from_creatures
        new_columns[concat_('from_illusions')] = player_defense & ser_from_illusions
        new_columns[concat_('from_all')] = player_defense

    new_df = pd.concat(new_columns.values(), axis=1, ignore_index=True)
    new_df.columns = new_columns.keys()

    new_df[['time', 'value']] = df[['time', 'value']]
    new_df['minutes'] = np.floor(new_df['time'] / 60)

    return new_df


def _get_column_names(columns: List[str]) -> Tuple[list[str], list[str]]:
    all_damage_columns = [x for x in columns if '|' in x]

    damage_name_columns = [x.split('|')[1] for x in columns if '|' in x]
    unique_damage_columns = list(set(damage_name_columns))
    return unique_damage_columns, all_damage_columns


def process_damage_windows(df: pd.DataFrame, MS: MatchSplitter, players: list) -> dict:
    damage_df = _split_damage_by_player(df, players)
    player_windows = MS.split_in_windows(damage_df, use_index=False)

    unique_name_columns, all_damage_columns = _get_column_names(damage_df.columns)

    agg_types = ['sum', 'mean', 'median', 'dmg_inst']

    data = create_player_windows(WINDOWS=DAMAGE_WINDOWS, WINDOW_BASE_DICT=WINDOWS_BASE_NULLS, AN=AN)

    for col in all_damage_columns:
        slot_str, damage_type_name = col.split('|')

        for item in player_windows:
            if not item['exists']:
                continue

            this_window = item['name']
            this_df = item['df']

            this_damage = this_df[this_df[col] == True]

            damage_sum, damage_mean_dmg_pm, damage_median_dmg_pm, damage_inst = 0, 0, 0, 0

            if not this_damage.empty:
                damage_inst = this_damage['value'].count()

                damage_sum = this_damage['value'].sum()
                damage_agged = this_damage.groupby('minutes')['value'].sum()

                correction_coef = len(damage_agged) / item['minutes']
                damage_median_dmg_pm = damage_agged.mean() * correction_coef
                damage_mean_dmg_pm = damage_agged.median() * correction_coef

            data['_' + slot_str][AN(damage_type_name + f'__{agg_types[0]}')][this_window] = PO(damage_sum)
            data['_' + slot_str][AN(damage_type_name + f'__{agg_types[1]}')][this_window] = PO(damage_mean_dmg_pm)
            data['_' + slot_str][AN(damage_type_name + f'__{agg_types[2]}')][this_window] = PO(damage_median_dmg_pm)
            data['_' + slot_str][AN(damage_type_name + f'__{agg_types[3]}')][this_window] = PO(damage_inst)

    return data
