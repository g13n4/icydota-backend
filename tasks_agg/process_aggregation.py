from typing import Dict, List, Tuple, Any, Callable

import numpy as np
import pandas as pd
from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session, select, col

from db import get_sync_db_session
from models import DataAggregationType, PerformanceWindowData, GamePerformance, PerformanceTotalData, ComparisonType, \
    PlayerGameData
from models import League, Game
from utils import get_sqlmodel_fields, to_dec


logger = get_task_logger(__name__)

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
def get_league_data(db_session: Session,
                    league_id: int,
                    total: bool,
                    comparison: bool,
                    flat: bool = False) -> List[Dict[str, Any]]:
    clauses = [Game.league_id == league_id]

    # TOTAL OR WINDOW DATA
    if total:
        model = PerformanceTotalData
        model_join = PerformanceTotalData.game_performance_id == GamePerformance.id
        fields = get_sqlmodel_fields(PerformanceTotalData, include_ids=False, to_set=True)
    else:
        model = PerformanceWindowData
        model_join = PerformanceWindowData.game_performance_id == GamePerformance.id
        fields = get_sqlmodel_fields(PerformanceWindowData, include_ids=True, to_set=True)

    select_fields = [model, PlayerGameData.hero_id, PlayerGameData.player_id, PlayerGameData.position_id]

    if comparison:
        select_fields.append(ComparisonType.flat)

    # QUERY BUILDING
    select_query = (select(*select_fields)
                    .join(GamePerformance, model_join)
                    .join(PlayerGameData, PlayerGameData.id == GamePerformance.player_game_data_id)
                    .join(Game, Game.id == PlayerGameData.game_id))

    # COMPARISON CHECK
    if comparison:
        select_query = select_query.join(ComparisonType, ComparisonType.id == GamePerformance.comparison_id)
        clauses.extend([
            GamePerformance.is_comparison == True,
            ComparisonType.basic == True,
            ComparisonType.flat == flat, ])
    else:
        clauses.append(GamePerformance.is_comparison == False)

    # FINAL QUERY
    select_query = select_query.where(*clauses)

    output = db_session.exec(select_query)
    return [{
        'position_id': position_id,
        'hero_id': hero_id,
        'player_id': player_id,
        **{"flat": flat},
        **model_obj.model_dump(include=fields), } for model_obj, hero_id, player_id, position_id, *flat in output.all()]


def process_comparison(data_flat: List[Dict[str, Any]],
                       data_perct: List[Dict[str, Any]],
                       process_function: Callable) \
        -> Tuple[Dict[str, Dict[int, List[Dict]]], Dict[str, Dict[int, List[Dict]]]]:

    flat_output = process_function(data_flat)
    perc_output = process_function(data_perct)
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
    fields = TOTAL_DATA_FIELDS if total else WINDOW_DATA_FIELDS
    new_obj = dict()
    for field in fields:
        new_obj[field] = item[field] and to_dec(item[field])

    if not total:
        new_obj['data_type_id'] = item['data_type_id']

    return data_type(**new_obj)


@shared_task(name="aggregate_league")
def process_aggregation(league_id: int):
    logger.info(f'Aggregating data for {league_id}')

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



    logger.info('Getting processing windows data')
    window_data = get_league_data(db_session=db_session, league_id=league_id, total=False, comparison=False)
    window_data = process_windows(data=window_data)


    logger.info('Getting processing windows comparison data')
    process_wd_flat = get_league_data(db_session=db_session, league_id=league_id, total=False, comparison=True, flat=True)
    process_wd_perc = get_league_data(db_session=db_session, league_id=league_id, total=False, comparison=True, flat=False)
    process_wd_flat, process_wd_perc = process_comparison(data_flat=process_wd_flat,
                                                          data_perct=process_wd_perc,
                                                          process_function=process_windows)

    logger.info('Getting processing totals data')
    process_td = get_league_data(db_session=db_session, league_id=league_id, total=True, comparison=False)
    process_td = process_totals(data=process_td)


    logger.info('Getting processing totals comparison data')
    process_td_flat = get_league_data(db_session=db_session, league_id=league_id, total=True, comparison=True, flat=True)
    process_td_perc = get_league_data(db_session=db_session, league_id=league_id, total=True, comparison=True, flat=False)
    process_td_flat,  process_td_perc = process_comparison(data_flat=process_td_flat,
                                                           data_perct=process_td_perc,
                                                           process_function=process_totals)



    logger.info('Writing data down')
    for agg_category in ['player_id', 'hero_id', 'position_id', ]:
        this_wd_data = window_data[agg_category]
        this_td_data = process_td[agg_category]

        for key in this_wd_data.keys():

            if agg_category == "player_id":
                agg_obj_data = {
                    'by_player': True,
                    'player_id': key,
                }

                comp_obj_data = {
                    'player_cpd_id': key,
                }
            elif agg_category == "hero_id":
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
