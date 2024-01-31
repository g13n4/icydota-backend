from functools import partial
from typing import Dict

import pandas as pd

from replay_parsing.modules import MatchSplitter
from ..processing_utils import add_data_type_name
from ..processing_utils import process_output
from ...windows import XP_WINDOWS


PROCESSED_DATA_NAME = 'xp'
AN = partial(add_data_type_name, text_to_add=PROCESSED_DATA_NAME)

xp_reasons = {
    0: 'other',
    1: 'xp for heroes',
    2: 'xp for creeps',
    3: 'xp for roshan',
}

PO = partial(process_output, allow_none=False)


def process_xp_windows(df: pd.DataFrame, MS: MatchSplitter, players_to_slot: Dict[str, int]) -> dict:
    df.replace(players_to_slot, inplace=True)
    xp_windows = MS.split_into_windows(df, use_index=False)

    data = MS.create_windows(WINDOWS=XP_WINDOWS, AN=AN)

    for window in xp_windows:
        if window['exists']:
            agged_df = window['df'].groupby(['targetname', 'xp_reason'])['value'].sum()
            for k, v in agged_df.to_dict().items():
                slot, gold_reason = k
                data[f'_{slot}'][AN(xp_reasons[gold_reason])][window['name']] = PO(v)

                if gold_reason in [1, 2] and v:
                    data[f'_{slot}'][AN(xp_reasons[gold_reason] + ' pm')][window['name']] = PO(v / window['minutes'])

    return data
