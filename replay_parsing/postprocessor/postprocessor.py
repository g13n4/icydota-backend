import copy
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from .columns_to_postprocess import LANE_COLUMNS, GAME_COLUMNS, SUM_TOTAL_DATA, AVERAGE_TOTAL_DATA, \
    COMPARE_DATA, COMPARE_DATA_SUPPORT
from ..modules import MatchPlayersData, MatchSplitter


def _flatten_for_pd(data: dict, db_names: list = None, ) -> list:
    if db_names is None:
        db_names = []

    return [{'slot': slot_k, 'data': ck, **{k: v for k, v in cv.items() if k not in db_names}}
            for slot_k, slot_v in data.items() for ck, cv in slot_v.items()]


def compare_position_performance(data_df: pd.DataFrame, MPD: MatchPlayersData, ) -> List[dict]:
    output = list()
    comparison_base = {
        'slot_comparandum': None,
        'position_comparandum': None,

        'slot_comparans': None,
        'position_comparans': None,

        'df_percent': None,
        'df_flat': None,
    }

    for player in MPD.get_all():
        for opponent_slot in player['opponents']:
            opponent = MPD[opponent_slot]

            compare_columns = COMPARE_DATA_SUPPORT if player['position'] > 3 else COMPARE_DATA
            comparison_df_index = pd.MultiIndex.from_tuples([(x, player['slot_text']) for x in compare_columns],
                                                            names=['data', 'slot'])

            comparison_df_percent = pd.DataFrame(np.nan,
                                                 index=comparison_df_index,
                                                 columns=data_df.columns).sort_index()

            comparison_df_flat = comparison_df_percent.copy()

            player_df_index = pd.MultiIndex.from_tuples([(x, player['slot_text']) for x in compare_columns],
                                                        names=['data', 'slot'])

            opponent_df_index = pd.MultiIndex.from_tuples([(x, opponent['slot_text']) for x in compare_columns],
                                                          names=['data', 'slot'])

            player_df = data_df.loc[player_df_index, :].sort_index()
            opponent_df = data_df.loc[opponent_df_index, :].sort_index()

            opponent_data = copy.deepcopy(comparison_base)

            with np.errstate(divide='ignore', invalid='ignore'):
                comparison_df_percent.loc[comparison_df_index, :] = player_df.values / opponent_df.values
                comparison_df_flat.loc[comparison_df_index, :] = player_df.values - opponent_df.values

            for comp_df in [comparison_df_percent, comparison_df_flat]:
                comp_df.reset_index(inplace=True)
                comp_df.replace([np.inf, -np.inf, np.nan], None, inplace=True)
                del comp_df['slot']

            opponent_data['df_percent'] = comparison_df_percent.copy()
            opponent_data['df_flat'] = comparison_df_flat.copy()

            opponent_data['slot_comparandum'] = player['slot']
            opponent_data['position_comparandum'] = player['position']

            opponent_data['slot_comparans'] = opponent['slot']
            opponent_data['position_comparans'] = opponent['position']

            output.append(opponent_data)

    return output


def fill_total_values(data_df: pd.DataFrame) -> pd.DataFrame:
    data_df.set_index(['data', 'slot'], inplace=True)

    data_df.loc[(SUM_TOTAL_DATA, 'ltotal')] = data_df.loc[(SUM_TOTAL_DATA, LANE_COLUMNS)].sum(axis=1)

    data_df.loc[(SUM_TOTAL_DATA, 'gtotal')] = data_df.loc[(SUM_TOTAL_DATA, GAME_COLUMNS)].sum(axis=1)

    data_df.loc[(AVERAGE_TOTAL_DATA, 'ltotal')] = data_df.loc[(AVERAGE_TOTAL_DATA, LANE_COLUMNS)].mean(axis=1)

    data_df.loc[(AVERAGE_TOTAL_DATA, 'gtotal')] = data_df.loc[(AVERAGE_TOTAL_DATA, GAME_COLUMNS)].mean(axis=1)

    return data_df


def postprocess_data(data: Dict[str, Dict[str, dict]],
                     MPD: MatchPlayersData,
                     MS: MatchSplitter, ) -> Tuple[pd.DataFrame, List[dict]]:
    data_df = pd.DataFrame(_flatten_for_pd(data, ['_parsing_name', '_db_name']), )

    total_columns = ['ltotal', 'gtotal']
    for col in total_columns:
        data_df[col] = pd.Series(dtype=np.float64)

    data_df.replace({None: np.nan}, inplace=True)
    [data_df[col].astype(np.float64) for col in data_df.columns if col in MS.window_values_names]

    filled_totals = fill_total_values(data_df)
    comparison_data = compare_position_performance(filled_totals.copy(), MPD)

    return filled_totals, comparison_data
