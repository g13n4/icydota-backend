from functools import partial
from typing import List, Tuple

import numpy as np
import pandas as pd

from constants.calculation.game.calculation_type.damage import DamageCalculations as Calculations
from modules.match_splitter import MatchSplitter
from modules.performance_data_processor import PerformanceDataProcessor
from replay_parsing.processors.processing_utils import process_output


PO = partial(process_output, allow_none=False)

# SUM | MEAN | MEDIAN | INSTANCES
DAMAGE_CALCULATION = {
    'with_summons': (
        Calculations.with_summons__sum,
        Calculations.with_summons__mean,
        Calculations.with_summons__median,
        Calculations.with_summons__dmg_inst,
    ),
    'to_heroes': (
        Calculations.to_heroes__sum,
        Calculations.to_heroes__mean,
        Calculations.to_heroes__median,
        Calculations.to_heroes__dmg_inst,
    ),

    'to_buildings': (
        Calculations.to_buildings__sum,
        Calculations.to_buildings__mean,
        Calculations.to_buildings__median,
        Calculations.to_buildings__dmg_inst,
    ),
    'to_creatures': (
        Calculations.to_creatures__sum,
        Calculations.to_creatures__mean,
        Calculations.to_creatures__median,
        Calculations.to_creatures__dmg_inst,
    ),
    'to_illusions': (
        Calculations.to_illusions__sum,
        Calculations.to_illusions__mean,
        Calculations.to_illusions__median,
        Calculations.to_illusions__dmg_inst,
    ),
    'to_all': (
        Calculations.to_all__sum,
        Calculations.to_all__mean,
        Calculations.to_all__median,
        Calculations.to_all__dmg_inst,
    ),

    'from_heroes': (
        Calculations.from_heroes__sum,
        Calculations.from_heroes__mean,
        Calculations.from_heroes__median,
        Calculations.from_heroes__dmg_inst,
    ),
    'from_buildings': (
        Calculations.from_buildings__sum,
        Calculations.from_buildings__mean,
        Calculations.from_buildings__median,
        Calculations.from_buildings__dmg_inst,
    ),
    'from_creatures': (
        Calculations.from_creatures__sum,
        Calculations.from_creatures__mean,
        Calculations.from_creatures__median,
        Calculations.from_creatures__dmg_inst,
    ),
    'from_illusions': (
        Calculations.from_illusions__sum,
        Calculations.from_illusions__mean,
        Calculations.from_illusions__median,
        Calculations.from_illusions__dmg_inst,
    ),
    'from_all': (
        Calculations.from_all__sum,
        Calculations.from_all__mean,
        Calculations.from_all__median,
        Calculations.from_all__dmg_inst,
    ),
}


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


def process_damage_windows(df: pd.DataFrame, MS: MatchSplitter, PDP: PerformanceDataProcessor, players: list, ) -> None:
    damage_df = _split_damage_by_player(df, players)
    player_windows = MS.split_into_windows(damage_df, use_index=False)

    unique_name_columns, all_damage_columns = _get_column_names(damage_df.columns)

    for col in all_damage_columns:
        slot_str, damage_type_name = col.split('|')
        slot = int(slot_str)

        for window in player_windows:
            if not window['exists']:
                continue

            this_df = window['df']
            this_damage = this_df[this_df[col] == True]

            damage_sum, damage_mean_dmg_pm, damage_median_dmg_pm, damage_inst = 0, 0, 0, 0

            if not this_damage.empty:
                damage_inst = this_damage['value'].count()

                damage_sum = this_damage['value'].sum()
                damage_agged = this_damage.groupby('minutes')['value'].sum()

                correction_coef = len(damage_agged) / window['minutes']
                damage_median_dmg_pm = damage_agged.mean() * correction_coef
                damage_mean_dmg_pm = damage_agged.median() * correction_coef

            sum_calc, mean_pm_calc, median_pm_calc, damage_inst_calc = DAMAGE_CALCULATION[damage_type_name]

            PDP.set_value(slot=slot, calculation=sum_calc, window_index=window['index'], value=PO(damage_sum))
            PDP.set_value(slot=slot, calculation=mean_pm_calc, window_index=window[
                'index'], value=PO(damage_mean_dmg_pm))
            PDP.set_value(slot=slot, calculation=median_pm_calc, window_index=window[
                'index'], value=PO(damage_median_dmg_pm))
            PDP.set_value(slot=slot, calculation=damage_inst_calc, window_index=window['index'], value=PO(damage_inst))
