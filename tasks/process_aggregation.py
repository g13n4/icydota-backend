from sqlmodel import Session, select, col
from functools import partial
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
from sqlmodel import Session, select, col

from db import get_sync_db_session
from models import DataAggregationType, League, PerformanceWindowData, GamePerformance, PerformanceTotalView, \
    PerformanceTotalData
from utils import get_sqlmodel_fields


# logger = get_task_logger(__name__)

# AGGREGATION FIELDS
AGG_REQUIRED_FIELDS = [
    'league_id',
    'dire_win',
    'team_id',
    'player_id',
    'position_id',
    'hero_id',
    'is_comparison',
]
WINDOW_DATA_FIELDS = get_sqlmodel_fields(PerformanceWindowData)  # w/o data_type_id bc it's a fk
TOTAL_DATA_FIELDS = get_sqlmodel_fields(PerformanceTotalView)

WINDOW_AGG_REQUIRED_FIELDS = WINDOW_DATA_FIELDS + AGG_REQUIRED_FIELDS + ['data_type_id']
TOTAL_AGG_REQUIRED_FIELDS = TOTAL_DATA_FIELDS + AGG_REQUIRED_FIELDS

# AGGREGATION FIELDS FOR COMPARISON
AGG_REQUIRED_COMPARISON_FIELDS = [
    'general',
    'player_cpd_id',
    'player_cps_id',
    'hero_cpd_id',
    'hero_cps_id',
    'pos_cpd_id',
    'pos_cps_id',
]


def add_performance_data(obj, fields: list, data, comp_obj=None) -> Dict[str, Any]:
    if not comp_obj:
        comp_obj = {}
    else:
        comp_obj = comp_obj.dict(include=set(AGG_REQUIRED_COMPARISON_FIELDS))

    return {**obj.dict(include=set(fields)), **data, **comp_obj}


def get_data(league_obj: League,
             ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]],]:
    total_data = []
    window_data = []

    total_data_comp = []
    window_data_comp = []

    for game in league_obj.games:
        for player_data in game.players_data:
            this_data = dict(
                player_id=player_data.player_id,
                hero_id=player_data.hero_id,
                position_id=player_data.position_id, )

            unpack_window_ = partial(add_performance_data, fields=WINDOW_AGG_REQUIRED_FIELDS, data=this_data)
            unpack_total_ = partial(add_performance_data, fields=TOTAL_AGG_REQUIRED_FIELDS, data=this_data)

            for performance in player_data.performance:
                for window_obj in performance.window_data:
                    if performance.comparison and not performance.comparison.general:
                        data = unpack_window_(obj=window_obj, comp_obj=performance.comparison)
                        window_data_comp.append(data)
                    else:
                        data = unpack_window_(obj=window_obj)
                        window_data.append(data)

                for total_obj in performance.total_data:
                    if performance.comparison:
                        data = unpack_total_(obj=total_obj, comp_obj=performance.comparison)
                        total_data_comp.append(data)
                    else:
                        data = unpack_total_(obj=total_obj)
                        total_data.append(data)

    return (total_data, window_data, total_data_comp, window_data_comp)


def get_amount_dict(df: pd.DataFrame, column: str, types_num: int) -> Dict[int, int]:
    return (df.groupby(column)[column].count() / types_num).to_dict()


def process_windows(data: List[Dict[str, Any]], ) -> Dict[str, Dict[int, List[Dict]]]:
    output = {
        'player_id': dict(),
        'hero_id': dict(),
        'position_id': dict(), }

    df = pd.DataFrame(data)

    unique_data_types = len(df['data_type_id'].unique())

    players = df.groupby(['player_id', 'data_type_id'])[WINDOW_DATA_FIELDS].mean()
    players_numbers: dict = get_amount_dict(df, 'player_id', unique_data_types)

    heroes = df.groupby(['hero_id', 'data_type_id'])[WINDOW_DATA_FIELDS].mean()
    heroes_numbers: dict = get_amount_dict(df, 'hero_id', unique_data_types)

    positions = df.groupby(['position_id', 'data_type_id'])[WINDOW_DATA_FIELDS].mean()

    for agg_data, agg_num, data_name in [(players, players_numbers, 'player_id',),
                                         (heroes, heroes_numbers, 'hero_id',),
                                         (positions, None, 'position_id'), ]:
        this_dict = output[data_name]
        this_num = agg_num or {x: 100 for x in range(1, 6)}

        agg_data.replace([np.inf, -np.inf, np.nan], None, inplace=True)

        for idx, this_values_dict in agg_data.reset_index().T.to_dict().items():
            key = this_values_dict[data_name]
            comp_size = True if this_num[key] < 3 else False

            if key not in this_dict:
                this_dict[key] = []
            this_dict[key].append(
                {**this_values_dict, 'less3': comp_size}
            )

    return output


def process_windows_comparison(data: List[Dict[str, Any]], ) -> Dict[Tuple[str, int, int], List[PerformanceWindowData]]:
    pass


def process_totals(data: List[Dict[str, Any]], ) -> Dict[Tuple[str, int, int], PerformanceTotalData]:
    pass


def process_totals_comparison(data: List[Dict[str, Any]], ) -> Dict[Tuple[str, int, int], PerformanceTotalData]:
    pass


# @shared_task(name='aggregate_league_data')
def process_aggregation(league_id: int):
    # logger.info(f'Aggregating data for {league_id}')

    db_session: Session = get_sync_db_session()

    # TODO: Compare the time of the latest aggregation created_at to the created_at of the last processed game

    league_obj = db_session.get(League, league_id)
    if not league_obj:
        raise ValueError("No such league in the database")

    aggregated_games_obj = db_session.exec(select(DataAggregationType)
                                           .where(DataAggregationType.league_id == league_id)).all()

    # deleting old aggregations
    if aggregated_games_obj:
        games_performance_objs = db_session.exec(select(GamePerformance)
                                                 .where(col(GamePerformance.aggregation_id)
                                                        .in_([x.id for x in aggregated_games_obj])))

        for game_performance_obj in games_performance_objs:
            db_session.delete(game_performance_obj)

        db_session.commit()
        del aggregated_games_obj

    # new aggregations

    total_data, window_data, total_data_comp, window_data_comp = get_data(league_obj)

    performance_window_ = process_windows(data=window_data)
    performance_window_comparison = process_windows_comparison(data=window_data_comp)

    performance_total_aggregated = process_totals(data=total_data)
    performance_total_aggregated = process_totals_comparison(data=total_data_comp)


process_aggregation(15475)
