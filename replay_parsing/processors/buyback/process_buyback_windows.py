from functools import partial

import pandas as pd

from constants.calculation.game.calculation_type.buyback import BuybackCalculations
from modules.match_splitter import MatchSplitter
from modules.performance_data_processor import PerformanceDataProcessor
from replay_parsing.processors.processing_utils import process_output


PO = partial(process_output, allow_none=False)


def process_buyback_windows(
        df: pd.DataFrame,
        MS: MatchSplitter,
        PDP: PerformanceDataProcessor,
) -> None:
    for slot, slot_df in MS.split_by_player(df):
        wards_windows = MS.split_into_windows(slot_df, use_index=False)
        for window in wards_windows:
            if window['exists']:
                window_df = window['df']

                window_size = len(window_df['time'])

                has_bb = window_df['has_bb'].sum()
                has_no_bb = window_df['has_no_bb'].sum()

                PDP.set_value(
                    slot=slot,
                    calculation=BuybackCalculations.has_buyback_time,
                    window_index=window['index'],
                    value=has_bb
                )
                PDP.set_value(
                    slot=slot,
                    calculation=BuybackCalculations.has_no_buyback_time,
                    window_index=window['index'],
                    value=has_no_bb
                )

                has_bb_perc = window_df['has_bb'].sum() / window_size
                has_no_bb_perc = window_df['has_no_bb'].sum() / window_size

                PDP.set_value(
                    slot=slot,
                    calculation=BuybackCalculations.has_buyback_percent,
                    window_index=window['index'],
                    value=has_bb_perc
                )
                PDP.set_value(
                    slot=slot,
                    calculation=BuybackCalculations.has_no_buyback_percent,
                    window_index=window['index'],
                    value=has_no_bb_perc
                )

                gold_loss = window_df['gold_loss'].sum()
                xp_loss = window_df['has_bb'].sum()

                PDP.set_value(
                    slot=slot,
                    calculation=BuybackCalculations.potential_gold_loss,
                    window_index=window['index'],
                    value=gold_loss
                )
                PDP.set_value(
                    slot=slot,
                    calculation=BuybackCalculations.potential_xp_loss,
                    window_index=window['index'],
                    value=xp_loss
                )
