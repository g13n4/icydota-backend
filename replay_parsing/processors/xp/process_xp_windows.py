from functools import partial
from typing import Dict

import pandas as pd

from constants.calculation.game.calculation_type.xp import XPCalculations as Calculations
from modules.match_splitter import MatchSplitter
from modules.performance_data_processor import PerformanceDataProcessor
from replay_parsing.processors.processing_utils import process_output


XP_REASONS = {
    1: (Calculations.xp_for_heroes, Calculations.xp_for_heroes_pm),
    2: (Calculations.xp_for_creeps, Calculations.xp_for_creeps_pm),
    3: (Calculations.xp_for_roshan, None),
}
#  0: (Calculations.other_reason, None),
#  7: weaver summons

PO = partial(process_output, allow_none=False)


def process_xp_windows(
        df: pd.DataFrame,
        MS: MatchSplitter,
        PDP: PerformanceDataProcessor,
        players_to_slot: Dict[str, int]
) -> None:
    df.replace(players_to_slot, inplace=True)
    xp_windows = MS.split_into_windows(df, use_index=False)

    for window in xp_windows:
        if window['exists']:
            agged_df = window['df'].groupby(['targetname', 'xp_reason'])['value'].sum()
            other_reason_dict = { x: 0 for x in range(10) }
            for k, value in agged_df.to_dict().items():
                slot, reason = k

                if reason not in XP_REASONS:
                    other_reason_dict[slot] += value

                else:
                    calc, calc_pm = XP_REASONS[reason]
                    PDP.set_value(slot=slot, calculation=calc.index, window_index=window['index'], value=value)

                    if calc_pm is not None and value:
                        PDP.set_value(slot=slot, calculation=calc_pm.index, window_index=window['index'], value=value)

            for slot, value in other_reason_dict.items():
                PDP.set_value(
                    slot=slot,
                    calculation=Calculations.other_reason,
                    window_index=window['index'],
                    value=value,
                )
