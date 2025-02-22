from functools import partial
from typing import Dict

import pandas as pd

from constants.calculation.game.calculation_type.gold import GoldCalculations as Calculations
from modules import MatchSplitter
from modules.performance_data_processor import PerformanceDataProcessor
from replay_parsing.processors import process_output


GOLD_REASON = {
    # 0: 'starting gold',
    1: (Calculations.death_penalty, Calculations.death_penalty_pm),
    6: (Calculations.gold_for_assist, Calculations.gold_for_assist_pm),
    11: (Calculations.gold_for_killing_buildings, Calculations.gold_for_killing_buildings_pm),
    12: (Calculations.gold_for_killing_heroes, Calculations.gold_for_killing_heroes_pm),
    13: (Calculations.gold_for_killing_creeps, Calculations.gold_for_killing_creeps_pm),
    14: (Calculations.gold_for_killing_neutrals, Calculations.gold_for_killing_neutrals_pm),
    15: (Calculations.gold_for_killing_roshan, Calculations.gold_for_killing_roshan_pm),
    16: (Calculations.gold_for_assisting_killing_couriers, Calculations.gold_for_assisting_killing_couriers_pm),
    17: (Calculations.gold_runes, Calculations.gold_runes_pm),
    19: (Calculations.gold_for_flag_bearer_and_dooms_devour, Calculations.gold_for_flag_bearer_and_dooms_devour_pm),
    20: (Calculations.gold_for_wards, Calculations.gold_for_wards_pm),
    21: (Calculations.gold_for_killing_couriers, Calculations.gold_for_killing_couriers_pm),
}

PO = partial(process_output, allow_none=False)


def process_gold_windows(
        df: pd.DataFrame,
        MS: MatchSplitter,
        PDP: PerformanceDataProcessor,
        players_to_slot: Dict[str, int]) -> None:
    df.replace(players_to_slot, inplace=True)
    wards_windows = MS.split_into_windows(df, use_index=False)

    for window in wards_windows:
        if window['exists']:
            agged_df = window['df'].groupby(['targetname', 'gold_reason'])['value'].sum()
            for k, value in agged_df.to_dict().items():
                slot, gold_reason = k
                if gold_reason == 0:
                    continue

                calc, calc_pm = GOLD_REASON[gold_reason]

                PDP.set_value(slot=slot, calculation=calc, window_index=window['index'], value=value)
                PDP.set_value(slot=slot, calculation=calc_pm, window_index=window['index'], value=value)
