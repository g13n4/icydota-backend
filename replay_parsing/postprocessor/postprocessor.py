import copy
from functools import partial, reduce
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd

from utils import get_both_slot_values
from .columns_to_postprocess import LANE_COLUMNS, GAME_COLUMNS, SUM_TOTAL_DATA, MAX_TOTAL_DATA, AVERAGE_TOTAL_DATA, \
    COMPARE_DATA_CORES, COMPARE_DATA_SUPPORT
from ..modules import MatchPlayersData, MatchSplitter


def _flatten_for_pd(data: dict, db_names: list = None, ) -> list:
    if db_names is None:
        db_names = []

    return [{'slot': slot_k, 'data': ck, **{k: v for k, v in cv.items() if k not in db_names}}
            for slot_k, slot_v in data.items() for ck, cv in slot_v.items()]


def _clean_df_inplace(df_: pd.DataFrame) -> None:
    df_.reset_index(inplace=True)
    df_.replace([np.inf, -np.inf, np.nan], None, inplace=True)
    del df_['slot']
    return None


def _get_df_slice(df: pd.DataFrame,  slot: int | str,  empty: bool = False,
                  index: Optional[list] = None, index_mult: Optional[pd.MultiIndex] = None) -> pd.DataFrame:
    slot_str, slot_int = get_both_slot_values(slot)
    if index_mult is not None:
        df_index = index_mult
    else:
        df_index = pd.MultiIndex.from_tuples([(x, slot_str) for x in index], names=['data', 'slot'])


    if empty:
        return pd.DataFrame(np.nan, index=df_index, columns=df.columns).sort_index()

    return df.loc[df_index, :].sort_index()


def _reduce_dfs(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    df1_mask = (df1.isna() & ~df2.isna()).copy()
    df2_mask = (df2.isna() & ~df1.isna()).copy()

    df1[df1_mask] = 0
    df2[df2_mask] = 0

    return df1.add(df2, fill_value=np.nan).copy()


def compare_position_performance(data_df: pd.DataFrame, MPD: MatchPlayersData, ) -> List[dict]:
    output = list()
    comparison_base = {
        'slot_comparandum': None,
        'position_comparandum': None,

        'slot_comparans': None,
        'position_comparans': None,

        'basic': True,

        'df_percent': None,
        'df_flat': None,
    }

    for player in MPD.get_all():
        get_df_slice = partial(_get_df_slice, df=data_df, index_mult=data_df.index)  # columns are turned into index

        player_df = get_df_slice(slot=player['slot'])

        this_player_data = copy.deepcopy(comparison_base)
        this_player_data['slot_comparandum'] = player['slot']
        this_player_data['position_comparandum'] = player['position']

        opponents_data_combined_percent = []
        opponents_data_combined_flat = []

        for opponent_slot in player['opponents']:
            opponent = MPD[opponent_slot]

            comparison_df_percent = get_df_slice(slot=player['slot'], empty=True)
            comparison_df_flat = comparison_df_percent.copy()

            opponent_df = get_df_slice(slot=opponent['slot'])

            this_opponent = copy.deepcopy(this_player_data)
            with np.errstate(divide='ignore', invalid='ignore'):
                for comp_df, type_func, comp_list, comp_name in [
                    (comparison_df_percent, np.divide, opponents_data_combined_percent, 'df_percent'),
                    (comparison_df_flat, np.subtract, opponents_data_combined_flat, 'df_flat'),
                ]:
                    comp_df.loc[:, :] = type_func(player_df.values, opponent_df.values)

                    # AGGREGATION PREPARATIONS
                    comp_list.append(opponent_df.copy())
                    if len(comp_list) > 1:
                        reduce(_reduce_dfs, comp_list)

                    # COPY AND CLEAN AFTER THE REDUCTION
                    _clean_df_inplace(comp_df)
                    this_opponent[comp_name] = comp_df.copy()

            this_opponent['slot_comparans'] = opponent['slot']
            this_opponent['position_comparans'] = opponent['position']

            output.append(this_opponent)

        # COMBINE AGGREGATED DATA
        if (opponents_number := len(player['opponents'])) != 1:

            this_player_agged_data = copy.deepcopy(this_player_data)
            this_player_agged_data['basic'] = False

            with np.errstate(divide='ignore', invalid='ignore'):
                for type_func, comp_list, comp_name in [
                    (np.divide, opponents_data_combined_percent, 'df_percent'),
                    (np.subtract, opponents_data_combined_flat, 'df_flat'),
                ]:
                    comparison_df_base = get_df_slice(slot=player['slot'], empty=True)
                    aggregated_df: pd.DataFrame = comp_list.pop()

                    comparison_df_base.loc[:, :] = type_func(player_df.values,
                                                             np.divide(aggregated_df.values, opponents_number))

                    _clean_df_inplace(comparison_df_base)
                    this_player_agged_data[comp_name] = comparison_df_base.copy()

            output.append(this_player_agged_data)

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
