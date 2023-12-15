import copy
import pandas as pd
from functools import partial
from replay_parsing.modules import MatchSplitter
from typing import Dict
from ..aggregations import WINDOWS_BASE_NULLS
from ..processing_utils import process_output
from functools import partial
from ..processing_utils import add_data_type_name


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
    xp_windows = MS.split_in_windows(df, use_index=False)

    data_item = {AN(x): copy.deepcopy(WINDOWS_BASE_NULLS) for x in xp_reasons.values()}
    data_item.update({AN(v + ' pm'): copy.deepcopy(WINDOWS_BASE_NULLS) for k, v in xp_reasons.items()
                      if k not in [0, 3]})

    data = {f'_{x}': copy.deepcopy(data_item) for x in range(10)}

    for window in xp_windows:
        if window['exists']:
            agged_df = window['df'].groupby(['targetname', 'xp_reason'])['value'].sum()
            for k, v in agged_df.to_dict().items():
                slot, gold_reason = k
                data[f'_{slot}'][AN(xp_reasons[gold_reason])][window['name']] = PO(v)

                if gold_reason in [1, 2] and v:
                    data[f'_{slot}'][AN(xp_reasons[gold_reason])][window['name']] = PO(v / window['minutes'])

    return data
