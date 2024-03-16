from typing import Dict, List, Tuple, Any, Callable

import numpy as np
import pandas as pd
from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session, select, col

from db import get_sync_db_session
from models import DataAggregationType, PerformanceWindowData, GamePerformance, PerformanceTotalData, ComparisonType, \
    PlayerGameData
from models import Game
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
                    positions: list,
                    total: bool,
                    flat: bool) -> List[Dict[str, Any]]:
    clauses = [Game.league_id == league_id,
               GamePerformance.is_comparison == True,
               ComparisonType.basic == True,
               ComparisonType.flat == flat,
               col(ComparisonType.pos_cpd_id).in_(positions)
               ]

    # TOTAL OR WINDOW DATA
    if total:
        model = PerformanceTotalData
        model_join = PerformanceTotalData.game_performance_id == GamePerformance.id
        fields = get_sqlmodel_fields(PerformanceTotalData, include_ids=False, to_set=True)
    else:
        model = PerformanceWindowData
        model_join = PerformanceWindowData.game_performance_id == GamePerformance.id
        fields = get_sqlmodel_fields(PerformanceWindowData, include_ids=True, to_set=True)

    select_fields = [model,
                     ComparisonType.flat,
                     ComparisonType.player_cpd_id,
                     ComparisonType.player_cps_id,
                     ComparisonType.hero_cpd_id,
                     ComparisonType.hero_cps_id,
                     ComparisonType.pos_cpd_id,
                     ComparisonType.pos_cps_id, ]


    # QUERY BUILDING
    select_query = (select(*select_fields)
                    .join(GamePerformance, model_join)
                    .join(PlayerGameData, PlayerGameData.id == GamePerformance.player_game_data_id)
                    .join(Game, Game.id == PlayerGameData.game_id)
                    .join(ComparisonType, ComparisonType.id == GamePerformance.comparison_id))

    # FINAL QUERY
    select_query = select_query.where(*clauses)

    output = db_session.exec(select_query)
    return [{
        'flat': selected_fields[0],
        'player_cpd_id': selected_fields[1],
        'player_cps_id': selected_fields[2],
        'hero_cpd_id': selected_fields[3],
        'hero_cps_id': selected_fields[4],
        'pos_cpd_id': selected_fields[5],
        'pos_cps_id': selected_fields[6],
        **model_obj.model_dump(include=fields), } for model_obj, *selected_fields in output.all()]


def process_comparison(data_flat: List[Dict[str, Any]],
                       data_perct: List[Dict[str, Any]],
                       process_function: Callable) \
        -> Tuple[Dict[str, Dict[int, List[Dict]]], Dict[str, Dict[int, List[Dict]]]]:

    flat_output = process_function(data_flat)
    perc_output = process_function(data_perct)
    return flat_output, perc_output


def get_amount_dict(df: pd.DataFrame, column: str, types_num: int) -> Dict[int, int]:
    return (df.groupby(column)[column].count() / types_num).to_dict()


def process_data(data: List[Dict[str, Any]], total: bool) -> Dict[str, Dict[int, List[Dict]]]:
    output = {
        'player': dict(),
        'hero': dict(), }

    df = pd.DataFrame(data)

    dti = []
    if total:
        fields = TOTAL_DATA_FIELDS
    else:
        fields = WINDOW_DATA_FIELDS
        dti = ['data_type_id']

    players = df.groupby(['player_cpd_id', 'player_cps_id'] + dti)[fields].mean()

    heroes = df.groupby(['hero_cpd_id', 'hero_cps_id'] + dti)[fields].mean()


    for agg_data, dict_name, cpd, cps in [(players, 'player', 'player_cpd_id', 'player_cps_id'),
                                          (heroes, 'hero', 'hero_cpd_id', 'hero_cps_id'), ]:
        this_dict = output[dict_name]

        agg_data.replace([np.inf, -np.inf, np.nan], None, inplace=True)

        for idx, this_values_dict in agg_data.reset_index().T.to_dict().items():
            cpd_id = this_values_dict[cpd]
            cps_id = this_values_dict[cps]

            key = (cpd_id, cps_id)

            if key not in this_dict:
                this_dict[key] = []
            this_dict[key].append(this_values_dict)

    return output


def _create_obj(item: dict, data_type, total: bool = False):
    if not total:
        new_obj = dict()
        for field in WINDOW_DATA_FIELDS:
            new_obj[field] = to_dec(item[field])
        new_obj['data_type_id'] = item['data_type_id']

    else:
        dt_properties: dict = data_type.schema()['properties']
        new_obj = dict()
        for field in TOTAL_DATA_FIELDS:
            field_type = dt_properties[field]['type']
            if field_type == 'integer':
                new_obj[field] = item[field] and int(item[field])
            else:
                new_obj[field] = item[field] and to_dec(item[field])

    return data_type(**new_obj)


@shared_task(name="create_cross_comparison")
def create_cross_comparison_aggregation(league_id: int):
    logger.info(f'Creating cross-comparison for {league_id}')

    db_session: Session = get_sync_db_session()

    # DELETING OLD DATA
    aggregated_games_obj = db_session.exec(select(DataAggregationType)
                                           .join(GamePerformance)
                                           .where(DataAggregationType.league_id == league_id,
                                                  GamePerformance.cross_comparison == True)).all()

    # deleting old aggregations
    if aggregated_games_obj:
        games_performance_objs = db_session.exec(select(GamePerformance)
                                                 .where(col(GamePerformance.aggregation_id)
                                                        .in_([x.id for x in aggregated_games_obj])))

        for game_performance_obj in games_performance_objs:
            db_session.delete(game_performance_obj)

        db_session.commit()
        del aggregated_games_obj


    # getting data
    for pos_name, positions in [('support', [4, 5]),
                                ('core', [1, 3]),
                                ('mid', [2]), ]:
        
    
        # TOTAL DATA
        logger.info(f'Getting processing totals data (flat) [{pos_name}]')
        process_td_flat = get_league_data(db_session=db_session, league_id=league_id, positions=positions, total=True, flat=True)
        PLAYER_TO_POS: Dict[int, int] = {item['player_cpd_id']: item['pos_cpd_id'] for item in process_td_flat}
        HERO_TO_POS: Dict[int, int] = {item['hero_cpd_id']: item['pos_cpd_id'] for item in process_td_flat}
        process_td_flat = process_data(data=process_td_flat, total=True)

        logger.info(f'Getting processing totals data (perc) [{pos_name}]')
        process_td_perc = get_league_data(db_session=db_session, league_id=league_id, positions=positions, total=True, flat=False)
        process_td_perc = process_data(data=process_td_perc, total=True)

        # WINDOW DATA
        logger.info(f'Getting processing windows data (flat) [{pos_name}]')
        window_wd_flat = get_league_data(db_session=db_session, league_id=league_id, positions=positions, total=False, flat=True)
        window_wd_flat = process_data(data=window_wd_flat, total=False)

        logger.info(f'Getting processing windows data (perc) [{pos_name}]')
        window_wd_perc = get_league_data(db_session=db_session, league_id=league_id, positions=positions, total=False, flat=False)
        window_wd_perc = process_data(data=window_wd_perc, total=False)

        # SETTING DATA
        logger.info(f'Writing down {pos_name} data')
        for agg_category in ['player', 'hero', ]:
            for wd_data, td_data, flat in [(window_wd_flat, process_td_flat, True),
                                           (window_wd_perc, process_td_perc, False), ]:

                this_wd_data = wd_data[agg_category]
                this_td_data = td_data[agg_category]

                for key in this_wd_data.keys():

                    (cpd, cps) = key

                    if agg_category == "player":
                        to_pos_dict = PLAYER_TO_POS

                        agg_obj_data = {
                            'pos_player_cross': True,
                            'by_player': True,
                            'player_id': cpd,
                            'player_cross_cps_id': cps,
                        }

                        comp_obj_data = {
                            'player_cpd_id': cpd,
                            'player_cps_id': cps,

                        }
                    else:
                        to_pos_dict = HERO_TO_POS

                        agg_obj_data = {
                            'pos_hero_cross': True,
                            'by_hero': True,
                            'hero_id': cpd,
                            'hero_cross_cps_id': cps,
                        }

                        comp_obj_data = {
                            'hero_cpd_id': cpd,
                            'hero_cps_id': cps,
                        }

                    # SETTING POSITION AGG
                    if pos_name == 'support':
                        agg_obj_data['sup_cross'] = True
                    elif pos_name == 'core':
                        agg_obj_data['carry_cross'] = True
                    else:
                        agg_obj_data['mid_cross'] = True


                    # FILLING OUT POSITION DATA
                    agg_obj_data['position_id'] = to_pos_dict[cpd]
                    agg_obj_data['position_cross_cps_id'] = to_pos_dict[cps]

                    comp_obj_data['pos_cpd_id'] = to_pos_dict[cpd]
                    comp_obj_data['pos_cpd_id'] = to_pos_dict[cps]

                    # TO PERFORMANCE DATA
                    wd_items = [_create_obj(x, PerformanceWindowData, total=False) for x in this_wd_data[key]]
                    td_items = [_create_obj(x, PerformanceTotalData, total=True) for x in this_td_data[key]]

                    DAT = DataAggregationType(
                        league_id=league_id,
                        less3=False,
                        **agg_obj_data,
                    )
                    db_session.add(DAT)

                    comp_type = ComparisonType(
                        flat=flat,
                        basic=False,
                        **comp_obj_data, )

                    GP = GamePerformance(
                        is_aggregation=True,
                        aggregation=DAT,
                        cross_comparison=True,

                        window_data=wd_items,
                        total_data=td_items,

                        is_comparison=True,
                        comparison=comp_type,
                    )
                    db_session.add(GP)

            db_session.commit()
