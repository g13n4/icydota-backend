import copy
from functools import partial, reduce
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd

from utils import get_both_slot_values
from .columns_to_postprocess import LANE_COLUMNS, GAME_COLUMNS, SUM_TOTAL_DATA, MAX_TOTAL_DATA, AVERAGE_TOTAL_DATA
from ..modules import MatchPlayersData, MatchSplitter


def _flatten_for_pd(data: dict, db_names: list = None, ) -> list:
    if db_names is None:
        db_names = []

    return [{'slot': slot_k, 'data': ck, **{k: v for k, v in cv.items() if k not in db_names}}
            for slot_k, slot_v in data.items() for ck, cv in slot_v.items()]


def _clean_df_inplace(df_: pd.DataFrame) -> None:
    df_.reset_index(inplace=True)
    df_.replace([np.inf, -np.inf, np.nan], None, inplace=True)
    return None


def _get_df_slice(df: pd.DataFrame,  slot: int | str,  empty: bool = False, ) -> pd.DataFrame:
    slot_str, slot_int = get_both_slot_values(slot)

    df = df.copy().reset_index()

    df_slice = df[df['slot'] == slot_str].copy()
    del df_slice['slot']

    df_slice.set_index('data', inplace=True)
    df_slice.sort_index(inplace=True)

    if empty:
        return pd.DataFrame(np.nan, index=df_slice.index, columns=df_slice.columns)

    return df_slice


def _reduce_dfs(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    df1_mask = (df1.isna() & ~df2.isna()).copy()
    df2_mask = (df2.isna() & ~df1.isna()).copy()

    df1[df1_mask] = 0
    df2[df2_mask] = 0

    return df1.add(df2, fill_value=np.nan).copy()


def add_df(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    return df1 + df2


def sub_df(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    return df1 - df2


def div_df(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    return df1 / df2


def compare_position_performance(data_df: pd.DataFrame, MPD: MatchPlayersData, ) -> Dict[int, list]:
    output = {x: [] for x in range(10)}

    comparison_base = {
        'slot_comparandum': None,
        'position_comparandum': None,

        'slot_comparans': None,
        'position_comparans': None,

        'basic': True,

        'is_flat': None,
        'df': None,
    }

    for player in MPD.get_all():
        player_slot = player['slot']
        get_df_slice = partial(_get_df_slice, df=data_df)  # columns are turned into index

        player_df = get_df_slice(slot=player_slot)

        this_player_data = copy.deepcopy(comparison_base)
        this_player_data['slot_comparandum'] = player['slot']
        this_player_data['position_comparandum'] = player['position']

        # FIRST - COMPARE PERFORMANCE ONE TO ONE
        for comp_name, is_flat, comp_func in [('percent', False, div_df), ('flat', True, sub_df), ]:
            aggregated_df = get_df_slice(slot=player_slot, empty=True)
            opponents_number = 0
            opponent_df = None
            this_player_data['is_flat'] = is_flat

            for opponent_slot in player['opponents']:
                opponent = MPD[opponent_slot]

                opponent_df = get_df_slice(slot=opponent['slot'])

                this_opponent = copy.deepcopy(this_player_data)
                with np.errstate(divide='ignore', invalid='ignore'):

                    comparison_df = comp_func(player_df, opponent_df)

                    # COPY AND CLEAN AFTER THE REDUCTION
                    _clean_df_inplace(comparison_df)
                    this_opponent['df'] = comparison_df.copy()

                    # AGGREGATION
                    aggregated_df = add_df(aggregated_df, opponent_df)

                this_opponent['slot_comparans'] = opponent['slot']
                this_opponent['position_comparans'] = opponent['position']

                output[player_slot].append(this_opponent)

                opponents_number += 1

            # COMBINE AGGREGATED DATA
            this_player_agged_data = copy.deepcopy(this_player_data)
            this_player_agged_data['basic'] = False

            with np.errstate(divide='ignore', invalid='ignore'):
                comparison_df = comp_func(player_df, opponent_df / opponents_number)

                _clean_df_inplace(comparison_df)
                this_player_agged_data['df'] = comparison_df.copy()

            output[player_slot].append(this_player_agged_data)

    return output


def fill_total_values(data_df: pd.DataFrame) -> pd.DataFrame:
    data_df.set_index(['data', 'slot'], inplace=True)

    data_df.loc[(SUM_TOTAL_DATA, 'ltotal')] = data_df.loc[(SUM_TOTAL_DATA, LANE_COLUMNS)].sum(axis=1)

    data_df.loc[(SUM_TOTAL_DATA, 'gtotal')] = data_df.loc[(SUM_TOTAL_DATA, GAME_COLUMNS)].sum(axis=1)


    data_df.loc[(MAX_TOTAL_DATA, 'ltotal')] = data_df.loc[(MAX_TOTAL_DATA, LANE_COLUMNS)].max(axis=1)

    data_df.loc[(MAX_TOTAL_DATA, 'gtotal')] = data_df.loc[(MAX_TOTAL_DATA, GAME_COLUMNS)].max(axis=1)


    data_df.loc[(AVERAGE_TOTAL_DATA, 'ltotal')] = data_df.loc[(AVERAGE_TOTAL_DATA, LANE_COLUMNS)].mean(axis=1)

    data_df.loc[(AVERAGE_TOTAL_DATA, 'gtotal')] = data_df.loc[(AVERAGE_TOTAL_DATA, GAME_COLUMNS)].mean(axis=1)

    return data_df


def postprocess_data(data: Dict[str, Dict[str, dict]],
                     MPD: MatchPlayersData,
                     MS: MatchSplitter, ) -> Tuple[pd.DataFrame, Dict[int, list]]:
    data_df = pd.DataFrame(_flatten_for_pd(data, ['_parsing_name', '_db_name']), )

    total_columns = ['ltotal', 'gtotal']
    for col in total_columns:
        data_df[col] = pd.Series(dtype=np.float64)

    data_df.replace({None: np.nan}, inplace=True)
    [data_df[col].astype(np.float64) for col in data_df.columns if col in MS.window_values_names]

    filled_totals = fill_total_values(data_df)
    comparison_data = compare_position_performance(filled_totals.copy(), MPD)

    return filled_totals, comparison_data
