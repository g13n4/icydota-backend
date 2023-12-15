from typing import Dict, List
from ..modules import MatchPlayersData
import copy

import numpy as np
import pandas as pd

from .columns_to_postprocess import LANE_COLUMNS, GAME_COLUMNS, SUM_TOTAL_DATA, AVERAGE_TOTAL_DATA, \
    COMPARE_DATA, COMPARE_DATA_SUPPORT, PERCENTAGE_DATA

# Add percentage data eventually ?

np.seterr(divide='ignore', invalid='ignore')

def _flatten_for_pd(data: dict) -> list:
    return [{'slot': slot_k, 'data': ck, **cv} for slot_k, slot_v in data.items()
            for ck, cv in slot_v.items()]


def compare_position_performance(data_df: pd.DataFrame, MPD: MatchPlayersData, ) -> dict:
    output = {f'_{x}': [] for x in range(10)}
    opponent_base = {
        'slot': None,
        'position': None,
        'position_name': None,
        'comparison': [],
        'comparison_name': '',
        'df': None
    }

    for player in MPD.get_all():
        for opponent_slot in player['opponents']:
            opponent = MPD[opponent_slot]

            compare_columns = COMPARE_DATA_SUPPORT if player['position'] > 3 else COMPARE_DATA
            comparison_df_index = pd.MultiIndex.from_tuples([(x, player['slot_text']) for x in compare_columns],
                                                            names=['data', 'slot'])

            comparison_df = pd.DataFrame(np.nan,
                                         index=comparison_df_index,
                                         columns=data_df.columns).sort_index()

            player_df_index = pd.MultiIndex.from_tuples([(x, player['slot_text']) for x in compare_columns],
                                                        names=['data', 'slot'])

            opponent_df_index = pd.MultiIndex.from_tuples([(x, opponent['slot_text']) for x in compare_columns],
                                                          names=['data', 'slot'])

            player_df = data_df.loc[player_df_index, :].sort_index()
            opponent_df = data_df.loc[opponent_df_index, :].sort_index()

            comparison_df.loc[comparison_df_index, :] = player_df.values / opponent_df.values

            opponent_data = copy.deepcopy(opponent_base)

            opponent_data['slot'] = opponent['slot']
            opponent_data['position'] = opponent['position']
            opponent_data['position_name'] = opponent['position_name']
            opponent_data['comparison'] = [player['slot'], opponent['slot']]
            opponent_data['comparison_name'] = f"{player['position_name']} to {opponent['position_name']}"

            comparison_df.reset_index(inplace=True)
            comparison_df.replace([np.inf, -np.inf], np.nan, inplace=True)

            nullable_values = ~comparison_df['data'].str.startswith('interval')

            comparison_df.loc[nullable_values, :] = comparison_df.loc[nullable_values, :].fillna(0)

            opponent_data['df'] = comparison_df.copy()

            output[player['slot_text']].append(opponent_data)

            return output


def fill_total_values(data_df: pd.DataFrame) -> pd.DataFrame:
    data_df['ltotal'] = np.nan
    data_df['gtotal'] = np.nan

    data_df.set_index(['data', 'slot'], inplace=True)

    data_df['ltotal'].loc[(SUM_TOTAL_DATA, slice(None))] = \
        data_df[LANE_COLUMNS].loc[(SUM_TOTAL_DATA, slice(None))].sum(axis=1)

    data_df['gtotal'].loc[(SUM_TOTAL_DATA, slice(None))] = \
        data_df[GAME_COLUMNS].loc[(SUM_TOTAL_DATA, slice(None))].sum(axis=1)

    data_df['ltotal'].loc[(AVERAGE_TOTAL_DATA, slice(None))] = \
        data_df[LANE_COLUMNS].loc[(AVERAGE_TOTAL_DATA, slice(None))].mean(axis=1)

    data_df['gtotal'].loc[(AVERAGE_TOTAL_DATA, slice(None))] = \
        data_df[GAME_COLUMNS].loc[(AVERAGE_TOTAL_DATA, slice(None))].mean(axis=1)

    return data_df


test_position = [1, 4, 5, 2, 3, 1, 2, 3, 4, 5]


def postprocess_data(data: Dict[str, Dict[str, dict]], MPD: MatchPlayersData) -> dict:
    MPD.set_position_from_list(test_position)

    data_df = pd.DataFrame(_flatten_for_pd(data))

    data_df = fill_total_values(data_df)

    comparison_data = compare_position_performance(data_df, MPD)

    return comparison_data
