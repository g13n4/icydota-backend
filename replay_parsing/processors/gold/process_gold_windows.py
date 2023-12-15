import copy
import pandas as pd
from functools import partial
from replay_parsing.modules import MatchSplitter
from typing import Dict
from ..aggregations import WINDOWS_BASE_NULLS
from ..processing_utils import process_output, add_data_type_name


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


PROCESSED_DATA_NAME = 'gold'
AN = partial(add_data_type_name, text_to_add=PROCESSED_DATA_NAME)
PO = partial(process_output, allow_none=False)

def process_gold_windows(df: pd.DataFrame, MS: MatchSplitter, players_to_slot: Dict[str, int]) -> dict:
    df.replace(players_to_slot, inplace=True)
    wards_windows = MS.split_in_windows(df, use_index=False)

    data_item = {AN(x): copy.deepcopy(WINDOWS_BASE_NULLS) for v in gold_reasons.values() for x in [v, v + ' pm']}
    data = {f'_{x}': copy.deepcopy(data_item) for x in range(10)}

    for window in wards_windows:
        if window['exists']:
            agged_df = window['df'].groupby(['targetname', 'gold_reason'])['value'].sum()
            for k, v in agged_df.to_dict().items():
                slot, xp_reason = k
                if xp_reason == 0:
                    continue
                data[f'_{slot}'][AN(gold_reasons[xp_reason])][window['name']] = PO(v)
                data[f'_{slot}'][AN(gold_reasons[xp_reason] + ' pm')][window['name']] = PO(v) / window['minutes']

    return data
