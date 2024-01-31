import re
from functools import partial
from typing import List

import pandas as pd

from replay_parsing.modules import MatchSplitter
from ..processing_utils import add_data_type_name
from ...windows import WARDS_WINDOWS, DEWARD_WINDOWS


PROCESSED_DATA_NAME = 'wards'
AN = partial(add_data_type_name, text_to_add=PROCESSED_DATA_NAME)


def process_wards_windows(df: pd.DataFrame, MS: MatchSplitter) -> dict:
    wards_windows = MS.split_into_windows(df, use_index=False)
    wards_data = MS.create_windows(WINDOWS=WARDS_WINDOWS, AN=AN)

    for window_df in wards_windows:
        if window_df['exists']:
            groupped_wdf = window_df['df'].groupby(['slot', 'type'])['time'].count()
            for k, v in groupped_wdf.to_dict().items():
                slot, ward_type = k
                wards_data[f'_{slot}'][AN(f'placed_wards_{ward_type}')][window_df['name']] = v

    return wards_data


def process_deward_windows(df: pd.DataFrame, MS: MatchSplitter,
                           players: List[dict], players_to_slot: dict) -> dict:
    df['slotname'] = df['slot'].replace({x['slot']: x['hero_npc_name'] for x in players})
    df['killed'] = df['slotname'] != df['attackername']

    df['attackerslot'] = df['attackername'].replace(players_to_slot)

    deward_windows = MS.split_into_windows(df, use_index=False)
    deward_data = MS.create_windows(WINDOWS=DEWARD_WINDOWS, AN=AN)

    for window_df in deward_windows:
        if window_df['exists']:
            groupped_wdf = window_df['df'].groupby(['slot', 'type'])['killed'].agg(['sum', 'count'])
            groupped_wdf['was_dewarded_perc'] = groupped_wdf['sum'] / groupped_wdf['count']
            groupped_wdf.rename({'count': 'was_dewarded'}, axis='columns', inplace=True)
            for name, item in groupped_wdf[['was_dewarded', 'was_dewarded_perc']].to_dict().items():
                for k, v in item.items():
                    slot, ward_type = k
                    new_ward_type = 'sen' if 'sen' in ward_type else 'obs'
                    deward_data[f'_{slot}'][AN(f'{name}_{new_ward_type}')][window_df['name']] = v

    for window_df in deward_windows:
        if window_df['exists']:
            groupped_wdf = window_df['df'].groupby(['attackerslot', 'type'])['killed'].agg('sum').to_dict()
            for k, v in groupped_wdf.items():
                slot, ward_type = k
                if not re.match(r'\d', str(slot)):  # the killer must be a hero
                    continue

                new_ward_type = 'sen' if 'sen' in ward_type else 'obs'
                deward_data[f'_{slot}'][AN(f'killed_{new_ward_type}')][window_df['name']] = v
                deward_data[f'_{slot}'][AN(f'killed_{new_ward_type}_pm')][window_df['name']] = v / window_df['minutes']

    return deward_data
