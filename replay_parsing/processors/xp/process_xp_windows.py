import copy
import pandas as pd
from replay_parsing.modules import MatchSplitter
from typing import Dict
from ..aggregations import WINDOWS_BASE_NULLS

xp_reasons = {
    0: 'other',
    1: 'xp for heroes',
    2: 'xp for creeps',
    3: 'xp for roshan',
}


def process_xp_windows(df: pd.DataFrame, MS: MatchSplitter, players_to_slot: Dict[str, int]) -> dict:
    df.replace(players_to_slot, inplace=True)
    xp_windows = MS.split_in_windows(df, use_index=False)

    data_item = {x: copy.deepcopy(WINDOWS_BASE_NULLS) for x in xp_reasons.values()}
    data_item.update({v + ' pm': copy.deepcopy(WINDOWS_BASE_NULLS) for k, v in xp_reasons.items()
                      if k not in [0, 3]})
    data = {f'_{x}': copy.deepcopy(data_item) for x in range(10)}

    for window in xp_windows:
        if window['exists']:
            agged_df = window['df'].groupby(['targetname', 'xp_reason'])['value'].sum()
            for k, v in agged_df.items():
                slot, gold_reason = k
                data[f'_{slot}'][xp_reasons[gold_reason]][window['name']] = v

                if gold_reason in [1, 2] and v:
                    data[f'_{slot}'][xp_reasons[gold_reason]][window['name']] = v / window['minutes']

    return data
