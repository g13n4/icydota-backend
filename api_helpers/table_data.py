import re
from typing import Optional, Tuple

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .model_field_info import TO_EXCLUDE_FOR_GAME, TO_EXCLUDE_FOR_LANE
from models import ComparisonType, DataAggregationType
from models import Hero, Player, Position
from models import PerformanceWindowData, GamePerformance, PlayerGameData, PerformanceTotalData
from utils import is_na_decimal


def combine_dict_fields(dict_: dict, cfi: dict) -> dict:
    dict_[cfi['field_name']] = cfi['pattern'].format(**dict_)
    dict_ = {k: v for k, v in dict_.items() if k not in cfi['fields_to_use']}
    return dict_

def modify_compared_to_field(item: dict, data_to_use: dict):
    this_hero = data_to_use[item['hero']]
    hero_name = this_hero['player']
    hero_pos = this_hero['hero']
    item['compared_to'] = f''


def _processing_db_output(output,
                          item_fields: dict,
                          exclude: list = None,
                          exists_total: bool = False,
                          combined_fields_data: Optional[list] = None) -> Tuple[list, list, bool]:
    if exclude is None:
        exclude = []

    if combined_fields_data is None:
        combined_fields_data = []

    is_data_comparison = 'compared_to' in item_fields

    processed_output = []
    data_values_info = dict()
    player_names = dict()
    for model_obj, *item_data in output.all():

        item = {k: item_data[v] for k, v in item_fields.items()}

        if is_data_comparison:
            player_names[item['hero']] = {
                'position': item['position'],
                'hero': item['hero'],
                'player': item['player'],
            }

        # if combined_fields_data:
        #     for cfdi in combined_fields_data:
        #         item = combine_dict_fields(item, cfdi)

        for model_obj_key, model_obj_value in model_obj.model_dump(exclude=set(exclude)).items():
            if (model_obj_key.lower() in ['game_performance_id', 'data_type_id', 'id'] or
                    (not exists_total and re.match(r'[g|l]total', model_obj_key, re.IGNORECASE))):
                continue
            if is_na_decimal(model_obj_value):
                model_obj_value = None

            item[model_obj_key] = model_obj_value

            # LOOKING FOR MIN AND MAX VALUES
            if model_obj_value is not None:
                # CREATE THE BASE DICT OR START COMPARING
                if model_obj_key not in data_values_info:
                    data_values_info[model_obj_key] = {
                        "max": model_obj_value,
                        "min": model_obj_value,
                        "diff": None, }
                else:

                    data_values_info[model_obj_key]["max"] = max(data_values_info[model_obj_key]["max"], model_obj_value)
                    data_values_info[model_obj_key]["min"] = min(data_values_info[model_obj_key]["min"], model_obj_value)

        processed_output.append(item)

    if is_data_comparison:
        [item for item in processed_output]

    # LOOKING FOR DIFFERENCE VALUES
    has_total = False
    for value_info_key in data_values_info.keys():
        mvi_max = data_values_info[value_info_key]["max"]
        mvi_min = data_values_info[value_info_key]["min"]

        data_values_info[value_info_key]["diff"] = mvi_max - mvi_min
        if re.match(r'[g|l]total', value_info_key):
            has_total = True

    return processed_output, [{**v, 'col': k} for k, v in data_values_info.items()], has_total



def build_gp_subquery(comparison: bool, cross_comparison: bool, aggregation: bool,):
    clauses = []
    fields = [GamePerformance.id, GamePerformance.player_game_data_id]

    clauses.append(GamePerformance.is_comparison == comparison)
    if comparison:
        fields.append(GamePerformance.comparison_id)

    clauses.append(GamePerformance.is_aggregation == aggregation)
    if aggregation:
        fields.append(GamePerformance.aggregation_id)

    clauses.append(GamePerformance.cross_comparison == cross_comparison)
    if cross_comparison:
        fields.append(GamePerformance.comparison_id)
        fields.append(GamePerformance.aggregation_id)

    subq = (select(*fields).where(*clauses)).subquery('gp_subq')
    return subq


async def get_performance_data(db_session: AsyncSession,
                               match_id: int,
                               data_type: int,
                               game_stage: str,
                               comparison: Optional[str],
                               flat: Optional[bool], ):
    is_comparison = comparison in ["player", "general"]
    clauses = [(PlayerGameData.game_id == match_id, -2)]
    gp_subq = build_gp_subquery(comparison=is_comparison, cross_comparison=False, aggregation=False)

    item_fields = {'position': 2,
                   'hero': 0,
                   'player': 1, }


    # TOTAL OR WINDOW DATA
    exclude = ['game_performance_id, id', 'data_type_id']
    if data_type == 0:
        model = PerformanceTotalData
    else:
        if game_stage == 'lane':
            exclude.extend(TO_EXCLUDE_FOR_LANE)
        elif game_stage == 'game':
            exclude.extend(TO_EXCLUDE_FOR_GAME)

        model = PerformanceWindowData
        clauses.append((PerformanceWindowData.data_type_id == data_type, -1))

    select_models = [model, Hero.name, Player.nickname, Position.name]
    if comparison == 'player':
        select_models.append(ComparisonType.pos_cps_id)
        item_fields['compared_to'] = 3


    # QUERY BUILDING
    select_query = (select(*select_models)
                    .join(gp_subq, onclause=gp_subq.c.id == model.game_performance_id)
                    .join(PlayerGameData, onclause=gp_subq.c.player_game_data_id == PlayerGameData.id)
                    .join(Position, onclause=PlayerGameData.position_id == Position.id)
                    .join(Hero, onclause=PlayerGameData.hero_id == Hero.id)
                    .join(Player, onclause=PlayerGameData.player_id == Player.account_id))

    # COMPARISON CHECK
    if is_comparison:
        select_query = select_query.join(ComparisonType, ComparisonType.id == gp_subq.c.comparison_id)

        clauses.extend([
            (ComparisonType.basic == (True if comparison == "player" else False), 1),
            (ComparisonType.flat == flat, 2), ])

    # SORTING CLAUSES TO FILTER
    clauses.sort(reverse=True, key=lambda x: x[1])
    # FINAL QUERY
    select_query = select_query.where(*[clause for clause, priority in clauses])

    output = await db_session.exec(select_query)

    data, limits, has_total_field = _processing_db_output(output=output, exclude=exclude, item_fields=item_fields, )

    return data, limits, has_total_field


async def get_aggregated_performance_data(db_session: AsyncSession,
                                          league_id: int,
                                          aggregation_type: str,
                                          data_type: int,
                                          game_stage: str,
                                          comparison: Optional[str],
                                          flat: Optional[bool], ):
    agg_type_dict = {
        "position": Position.name,
        "hero": Hero.name,
        "player": Player.nickname,
    }


    clauses = [DataAggregationType.league_id == league_id,
               GamePerformance.is_aggregation == True, ]

    exclude = ['game_performance_id, id']
    # TOTAL OR WINDOW DATA
    if data_type == 0:
        model = PerformanceTotalData
    else:
        if game_stage == 'lane':
            exclude.extend(TO_EXCLUDE_FOR_LANE)
        elif game_stage == 'game':
            exclude.extend(TO_EXCLUDE_FOR_GAME)

        model = PerformanceWindowData
        clauses.append(PerformanceWindowData.data_type_id == data_type)


    # QUERY BUILDING
    select_query = (select(*[model, agg_type_dict[aggregation_type]])
                    .join(GamePerformance)
                    .join(DataAggregationType))

    # COMPARISON
    if comparison in ["general"]:
        select_query = select_query.join(ComparisonType, ComparisonType.id == GamePerformance.comparison_id)
        clauses.extend([
            GamePerformance.is_comparison == True,
            GamePerformance.cross_comparison == False,
            ComparisonType.flat == flat, ])
    else:
        clauses.append(GamePerformance.is_comparison == False)

    # AGGREGATION
    if aggregation_type == "position":
        select_query = select_query.join(Position, onclause=DataAggregationType.position_id == Position.id)
        clauses.append(DataAggregationType.by_position == True)
    elif aggregation_type == "player":
        select_query = select_query.join(Player, onclause=DataAggregationType.player_id == Player.account_id)
        clauses.append(DataAggregationType.by_player == True)
    else:
        select_query = select_query.join(Hero, onclause=DataAggregationType.hero_id == Hero.id)
        clauses.append(DataAggregationType.by_hero == True)

    # FINAL QUERY
    select_query = select_query.where(*clauses)

    output = await db_session.exec(select_query)

    data, limits, has_total_field = _processing_db_output(output=output, item_fields={aggregation_type: 0, }, exclude=exclude, )

    return data, limits, has_total_field


def _update_variable(dict_: dict, key_: int | str, new_var: int | str):
    dict_.update({key_: new_var})
    return dict_


def _order_dict(dict_: dict, field: str) -> dict:
    return {k: v for k, v in sorted(dict_.items(), key=lambda item: str(item[1][field]).lower(), )}


async def get_cross_comparison_performance_data(db_session: AsyncSession,
                                                league_id: int,
                                                aggregation_type: str,
                                                position: str,
                                                data_field: str,
                                                data_type: int,
                                                flat: bool, ):
    fields_dict = {
        "hero": [Hero.name, Hero.id,  DataAggregationType.hero_cross_cps_id],
        "player": [Player.nickname, Player.account_id,  DataAggregationType.player_cross_cps_id],
    }


    clauses = [DataAggregationType.league_id == league_id,
               GamePerformance.cross_comparison == True,
               ComparisonType.flat == flat, ]

    select_fields = fields_dict[aggregation_type]

    # TOTAL OR WINDOW DATA
    if data_type == 0:
        model = PerformanceTotalData
    else:
        model = PerformanceWindowData
        clauses.append(model.data_type_id == data_type)

    select_fields.append(getattr(model, data_field))

    # QUERY BUILDING
    select_query = (select(*select_fields)
                    .join(GamePerformance, GamePerformance.id == model.game_performance_id)
                    .join(DataAggregationType, DataAggregationType.id == GamePerformance.aggregation_id)
                    .join(ComparisonType, ComparisonType.id == GamePerformance.comparison_id))

    # AGGREGATION
    if aggregation_type == "player":
        select_query = select_query.join(Player, onclause=DataAggregationType.player_id == Player.account_id)
        clauses.append(DataAggregationType.pos_player_cross == True)
    else:
        select_query = select_query.join(Hero, onclause=DataAggregationType.hero_id == Hero.id)
        clauses.append(DataAggregationType.pos_hero_cross == True)

    if position == 'support':
        clauses.append(DataAggregationType.sup_cross == True)
    elif position == 'core':
        clauses.append(DataAggregationType.carry_cross == True)
    else:
        clauses.append(DataAggregationType.mid_cross == True)

    # FINAL QUERY
    select_query = select_query.where(*clauses)

    query_output = await db_session.exec(select_query)

    # REFORMATTED _processing_db_output
    output_dict = dict()
    data_values_info = dict()
    rename_dict = dict()
    # hero/player name | id in db | id in db of the comparans player/hero
    for this_actor, this_actor_id, this_cps, value in query_output.all():
        rename_dict[this_actor_id] = this_actor

        if this_actor not in output_dict:
            output_dict[this_actor] = {
                aggregation_type: this_actor,
            }

        if is_na_decimal(value):
            value = None

        output_dict[this_actor][this_cps] = value

        if value is None:
            continue

        if this_cps not in data_values_info:
            data_values_info[this_cps] = {
                "max": value,
                "min": value,
                "diff": None, }
        else:
            data_values_info[this_cps]["max"] = max(
                data_values_info[this_cps]["max"], value)
            data_values_info[this_cps]["min"] = min(
                data_values_info[this_cps]["min"], value)

    # LOOKING FOR DIFFERENCE VALUES
    for value_info_key in data_values_info.keys():
        mvi_max = data_values_info[value_info_key]["max"]
        mvi_min = data_values_info[value_info_key]["min"]

        data_values_info[value_info_key]["diff"] = mvi_max - mvi_min

    ordered_names = sorted(rename_dict.values(), key=lambda x: (x).lower())
    # REMOVING OLD VALUES FROM DICTIONARY
    new_output = dict()
    for item_name, item in output_dict.items():
        temp_dict = dict()
        for k, v in item.items():  # id / value
            cps_name = rename_dict.get(k, k)
            temp_dict[cps_name] = v

        new_output[item_name] = {(o_name if o_name != item_name else aggregation_type):
                                     (temp_dict.get(o_name, None) if o_name != item_name else temp_dict[aggregation_type])
                                 for o_name in ordered_names }

    new_output = _order_dict(new_output, aggregation_type)

    return (new_output, [{**v, 'col': rename_dict[k]} for k, v in data_values_info.items()])
