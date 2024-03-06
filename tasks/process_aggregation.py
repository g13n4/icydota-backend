from sqlmodel import Session, select, col
from functools import partial
from typing import Dict, List, Tuple, Any, Optional, Callable

import numpy as np
import pandas as pd
from sqlmodel import Session, select, col

from db import get_sync_db_session
from models import DataAggregationType, League, PerformanceWindowData, GamePerformance, PerformanceTotalView, \
    PerformanceTotalData, ComparisonType
from utils import get_sqlmodel_fields, to_dec


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
TOTAL_DATA_FIELDS = get_sqlmodel_fields(PerformanceTotalData)

WINDOW_AGG_REQUIRED_FIELDS = WINDOW_DATA_FIELDS + AGG_REQUIRED_FIELDS + ['data_type_id']
TOTAL_AGG_REQUIRED_FIELDS = TOTAL_DATA_FIELDS + AGG_REQUIRED_FIELDS

# AGGREGATION FIELDS FOR COMPARISON
AGG_REQUIRED_COMPARISON_FIELDS = [
    'basic',
    'flat',
    'player_cpd_id',
    'player_cps_id',
    'hero_cpd_id',
    'hero_cps_id',
    'pos_cpd_id',
    'pos_cps_id',
]


def add_performance_data(obj, fields: list, data, comp_obj: Optional[ComparisonType] = None) -> Dict[str, Any]:
    if not comp_obj:
        comp_obj = {}
    else:
        comp_obj = comp_obj.dict(include=set(AGG_REQUIRED_COMPARISON_FIELDS))

    return {**obj.dict(include=set(fields)), **data, **comp_obj}


def get_data(league_obj: League,
             ) -> Tuple[
    List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, set]]:
    total_data = []
    window_data = []

    total_data_comp = []
    window_data_comp = []

    keys = {
        'player_id': set(),
        'hero_id': set(),
        'position_id': set(),
    }

    for game in league_obj.games:
        for player_data in game.players_data:
            this_data = dict(
                player_id=player_data.player_id,
                hero_id=player_data.hero_id,
                position_id=player_data.position_id, )

            keys['player_id'].add(player_data.player_id)
            keys['hero_id'].add(player_data.hero_id)
            keys['position_id'].add(player_data.position_id)

            unpack_window_ = partial(add_performance_data, fields=WINDOW_AGG_REQUIRED_FIELDS, data=this_data)
            unpack_total_ = partial(add_performance_data, fields=TOTAL_AGG_REQUIRED_FIELDS, data=this_data)

            for performance in player_data.performance:
                for pdata, unpack_func, data, data_comp in \
                        [(performance.window_data, unpack_window_, window_data, window_data_comp),
                         (performance.total_data, unpack_total_, total_data, total_data_comp)]:
                    for obj in pdata:
                        if performance.comparison and not performance.comparison.basic:
                            continue

                        unpacked_data = unpack_func(obj=obj, comp_obj=performance.comparison)
                        if performance.comparison:
                            data_comp.append(unpacked_data)
                        else:
                            data.append(unpacked_data)

    return (total_data, window_data, total_data_comp, window_data_comp, keys)


def process_comparison(data: List[Dict[str, Any]], process_function: Callable) \
        -> Tuple[Dict[str, Dict[int, List[Dict]]], Dict[str, Dict[int, List[Dict]]]]:
    flat_data = []
    perc_data = []
    for obj in data:
        if obj['flat']:
            flat_data.append(obj)
        else:
            perc_data.append(obj)

    flat_output = process_function(flat_data)
    perc_output = process_function(perc_data)
    return flat_output, perc_output


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


def process_totals(data: List[Dict[str, Any]], ) -> Dict[str, Dict[int, List[Dict]]]:
    output = {
        'player_id': dict(),
        'hero_id': dict(),
        'position_id': dict(), }

    df = pd.DataFrame(data)

    players = df.groupby('player_id')[TOTAL_DATA_FIELDS].mean()

    heroes = df.groupby('hero_id')[TOTAL_DATA_FIELDS].mean()

    positions = df.groupby('position_id')[TOTAL_DATA_FIELDS].mean()

    for agg_data, data_name in [(players, 'player_id',),
                                (heroes, 'hero_id',),
                                (positions, 'position_id'), ]:
        this_dict = output[data_name]

        agg_data.replace([np.inf, -np.inf, np.nan], None, inplace=True)

        for idx, this_values_dict in agg_data.reset_index().T.to_dict().items():
            key = this_values_dict[data_name]

            if key not in this_dict:
                this_dict[key] = []
            this_dict[key].append(this_values_dict)

    return output


def _create_obj(item: dict, data_type, total: bool = False):
    if not total:
        new_obj = dict()
        for field in WINDOW_DATA_FIELDS:
            new_obj[field] = to_dec(item[field])

    else:
        dt_properties: dict = data_type.schema()['properties']
        new_obj = dict()
        for field in TOTAL_DATA_FIELDS:
            field_type = dt_properties[field]['type']
            if field_type == 'integer':
                new_obj[field] = item[field] and int(item[field])
            else:
                new_obj[field] = item[field] and to_dec(item[field])

    new_obj['data_type_id'] = item['data_type_id']
    return data_type(**new_obj)


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
    print('Getting league data')
    total_data, window_data, total_data_comp, window_data_comp, id_keys = get_data(league_obj)

    print('Getting processing windows data')
    process_wd = process_windows(data=window_data)
    del window_data

    print('Getting processing windows comparison data')
    process_wd_flat, process_wd_perc = process_comparison(data=window_data_comp, process_function=process_windows)
    del window_data_comp

    print('Getting processing totals data')
    process_td = process_totals(data=total_data)
    del total_data

    print('Getting processing totals comparison data')
    process_td_flat, process_td_perc = process_comparison(data=total_data_comp, process_function=process_totals)
    del total_data_comp

    print('Writing data down')
    for agg_cat_idx, agg_category in enumerate(['player_id', 'hero_id', 'position_id', ]):
        this_wd_data = process_wd[agg_category]
        this_td_data = process_td[agg_category]

        for key in this_wd_data.keys():

            if agg_cat_idx == 0:
                agg_obj_data = {
                    'by_player': True,
                    'player_id': key,
                }

                comp_obj_data = {
                    'player_cpd_id': key,
                }
            elif agg_cat_idx == 1:
                agg_obj_data = {
                    'by_hero': True,
                    'hero_id': key,
                }

                comp_obj_data = {
                    'hero_cpd_id': key,
                }
            else:
                agg_obj_data = {
                    'by_position': True,
                    'position_id': key,
                }

                comp_obj_data = {
                    'pos_cpd_id': key,
                }

            less3 = this_wd_data[key][0]['less3']

            wd_items = [_create_obj(x, PerformanceWindowData, total=False) for x in this_wd_data[key]]
            td_items = [_create_obj(x, PerformanceTotalData, total=True) for x in this_td_data[key]]

            DAT = DataAggregationType(
                league_id=league_id,
                less3=less3,
                **agg_obj_data,
            )
            db_session.add(DAT)

            GP = GamePerformance(
                is_aggregation=True,
                aggregation=DAT,
                window_data=wd_items,
                total_data=td_items,

            )
            db_session.add(GP)

            for prcs_td_data, prcs_wd_data, is_flat in [(process_td_flat, process_wd_flat, True),
                                                        (process_td_perc, process_wd_perc, False), ]:
                this_prcs_wd_data = prcs_wd_data[agg_category]
                this_prcs_td_data = prcs_td_data[agg_category]

                wd_prcs_items = [_create_obj(x, PerformanceWindowData, total=False) for x in this_prcs_wd_data[key]]
                td_prcs_items = [_create_obj(x, PerformanceTotalData, total=True) for x in this_prcs_td_data[key]]

                comp_type = ComparisonType(
                    flat=is_flat,
                    basic=False,
                    **comp_obj_data, )

                GP_comp = GamePerformance(
                    is_aggregation=True,
                    aggregation=DAT,

                    window_data=wd_prcs_items,
                    total_data=td_prcs_items,

                    is_comparison=True,
                    comparison=comp_type,

                )
                db_session.add(GP_comp)

    db_session.commit()


process_aggregation(15475)
