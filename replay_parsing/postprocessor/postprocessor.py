import copy
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from .columns_to_postprocess import LANE_COLUMNS, GAME_COLUMNS, SUM_TOTAL_DATA, AVERAGE_TOTAL_DATA, \
    COMPARE_DATA, COMPARE_DATA_SUPPORT
from ..modules import MatchPlayersData

# Add percentage data eventually ?

np.seterr(divide='ignore', invalid='ignore')

def _flatten_for_pd(data: dict) -> list:
    return [{'slot': slot_k, 'data': ck, **cv} for slot_k, slot_v in data.items()
            for ck, cv in slot_v.items()]


def compare_position_performance(data_df: pd.DataFrame, MPD: MatchPlayersData, ) -> List[dict]:
    output = list()
    opponent_base = {
        'slot_comparandum': None,
        'position_comparandum': None,

        'slot_comparans': None,
        'position_comparans': None,

        'comparison': [],
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

            opponent_data['slot_comparandum'] = player['slot']
            opponent_data['position_comparandum'] = player['position']

            opponent_data['slot_comparans'] = opponent['slot']
            opponent_data['position_comparans'] = opponent['position']

            comparison_df.reset_index(inplace=True)
            comparison_df.replace([np.inf, -np.inf], np.nan, inplace=True)

            nullable_values = ~comparison_df['data'].str.startswith('interval')

            comparison_df.loc[nullable_values, :] = comparison_df.loc[nullable_values, :].fillna(0)

            del comparison_df['slot']
            opponent_data['df'] = comparison_df.copy()

            output.append(opponent_data)

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


def postprocess_data(data: Dict[str, Dict[str, dict]], MPD: MatchPlayersData) -> Tuple[pd.DataFrame, List[dict]]:
    data_df = pd.DataFrame(_flatten_for_pd(data))

    filled_totals = fill_total_values(data_df)

    comparison_data = compare_position_performance(filled_totals.copy(), MPD)

    return filled_totals, comparison_data
