import copy
import pandas as pd
from replay_parsing.modules import MatchSplitter
from typing import Dict
from ..aggregations import WINDOWS_BASE_NULLS

gold_reasons = {
    # 0: 'starting gold',
    1: 'death penalty',
    6: 'gold for assist',
    11: 'gold for killing buildings',
    12: 'gold for killing heroes',
    13: 'gold for killing creeps',
    14: 'gold for killing neutrals',
    15: 'gold for killing roshan',
    16: 'gold for assisting killing couriers',
    17: 'gold runes',
    19: 'gold for flag bearer (and doom\'s devour)',
    20: 'gold for wards',
    21: 'gold for killing couriers',
}


def process_gold_windows(df: pd.DataFrame, MS: MatchSplitter, players_to_slot: Dict[str, int]) -> dict:
    df.replace(players_to_slot, inplace=True)
    wards_windows = MS.split_in_windows(df, use_index=False)

    data_item = {x: copy.deepcopy(WINDOWS_BASE_NULLS) for x in gold_reasons.values()}
    data = {f'_{x}': copy.deepcopy(data_item) for x in range(10)}

    for window in wards_windows:
        if window['exists']:
            agged_df = window['df'].groupby(['targetname', 'gold_reason'])['value'].sum()
            for k, v in agged_df.items():
                slot, xp_reason = k
                if xp_reason == 0:
                    continue
                data[f'_{slot}'][gold_reasons[xp_reason]][window['name']] = v

    return data
