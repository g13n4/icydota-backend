import copy
import re
import pandas as pd
from replay_parsing.modules import MatchSplitter
from typing import List
from ..aggregations import WINDOWS_BASE_NULLS


def process_wards_windows(df: pd.DataFrame, MS: MatchSplitter) -> dict:
    wards_windows = MS.split_in_windows(df, use_index=False)
    wards_data = {f'_{y}': {f'placed_wards_{x}': copy.deepcopy(WINDOWS_BASE_NULLS) for x in ['sen', 'obs']}
                  for y in range(10)}
    for window_df in wards_windows:
        if window_df['exists']:
            groupped_wdf = window_df['df'].groupby(['slot', 'type'])['time'].count()
            for k, v in groupped_wdf.items():
                slot, ward_type = k
                wards_data[f'_{slot}'][f'placed_wards_{ward_type}'][window_df['name']] = v

    return wards_data

def process_deward_windows(df: pd.DataFrame, MS: MatchSplitter,
                           players: List[dict], players_to_slot: dict) -> dict:
    df['slotname'] = df['slot'].replace({x['slot']: x['hero_npc_name'] for x in players})
    df['killed'] = df['slotname'] != df['attackername']

    df['attackerslot'] = df['attackername'].replace(players_to_slot)

    deward_windows = MS.split_in_windows(df, use_index=False)
    player_data = {x: copy.deepcopy(WINDOWS_BASE_NULLS) for x in ['was_dewarded_sen', 'was_dewarded_obs',
                                                                  'was_dewarded_perc_sen', 'was_dewarded_perc_obs',
                                                                  'killed_sen', 'killed_obs',
                                                                  'killed_sen_pm', 'killed_obs_pm', ]}
    deward_data = {f'_{y}': player_data for y in range(10)}

    for window_df in deward_windows:
        if window_df['exists']:
            groupped_wdf = window_df['df'].groupby(['slot', 'type'])['killed'].agg(['sum', 'count'])
            groupped_wdf['was_dewarded_perc'] = groupped_wdf['sum'] / groupped_wdf['count']
            groupped_wdf.rename({'count': 'was_dewarded'}, axis='columns', inplace=True)
            for name, item in groupped_wdf[['was_dewarded', 'was_dewarded_perc']].items():
                for k, v in item.items():
                    slot, ward_type = k
                    new_ward_type = 'sen' if 'sen' in ward_type else 'obs'
                    deward_data[f'_{slot}'][f'{name}_{new_ward_type}'][window_df['name']] = v

    for window_df in deward_windows:
        if window_df['exists']:
            groupped_wdf = window_df['df'].groupby(['attackerslot', 'type'])['killed'].agg('sum').to_dict()
            for k, v in groupped_wdf.items():
                slot, ward_type = k
                if not re.match(r'\d', str(slot)):  # the killer must be a hero
                    continue

                new_ward_type = 'sen' if 'sen' in ward_type else 'obs'
                deward_data[f'_{slot}'][f'killed_{new_ward_type}'][window_df['name']] = v
                deward_data[f'_{slot}'][f'killed_{new_ward_type}_pm'][window_df['name']] = v / window_df['length']

    return deward_data