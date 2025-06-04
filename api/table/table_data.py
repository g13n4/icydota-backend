from collections import abc
from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from api.table.helpers import process_db_output, extract_window_data_for_field
from constants.api import PoTEnum
from modules.minmax_finder import TableMinMaxFinder
from modules.query_creators.performance.aggregation_performance_query_creator import \
    APIAggregationPerformanceQueryCreator
from modules.query_creators.performance.crosscomparison_performance_query_creator import \
    APICrossComparisonPerformanceQueryCreator
from modules.query_creators.performance.match_performance_query_creator import APIMatchPerformanceQueryCreator
from utils import is_na_decimal


async def get_performance_data(
        db_session: AsyncSession,
        pot: PoTEnum,
        match_id: int,
        data_type: int,
        game_stage: str,
):

    PQC = APIMatchPerformanceQueryCreator()
    select_query = PQC.get_match_query(match_id=match_id, calculation_type_id=data_type, pot=pot)
    model_names = PQC.get_model_names()
    query_output = await db_session.exec(select_query)

    data, value_mapping, has_total_field = process_db_output(
        query=query_output,
        model_names=model_names,
        game_stage=game_stage,
        pot=pot,
        req_type="match",
        data_model_name=PQC.data_model_name,
    )

    return data, value_mapping, has_total_field, PQC.get_model_names(only_header=True)


async def get_performance_data_comparison(
        db_session: AsyncSession,
        pot: PoTEnum,
        match_id: int,
        calculation_type_id: int,
        game_stage: str,
        basic: bool,
        flat: bool | None,
):
    PQC = APIMatchPerformanceQueryCreator()
    select_query = PQC.get_match_comparison_query(
        match_id=match_id,
        calculation_type_id=calculation_type_id,
        pot=pot,
        basic=basic,
        is_flat=flat,
    )
    model_names = PQC.get_model_names()
    query_output = await db_session.exec(select_query)

    data, value_mapping, has_total_field = process_db_output(
        query=query_output,
        model_names=model_names,
        game_stage=game_stage,
        pot=pot,
        req_type="match",
        data_model_name=PQC.data_model_name,
    )

    return data, value_mapping, has_total_field, PQC.get_model_names(only_header=True)


async def get_aggregated_performance_data(
        db_session: AsyncSession,
        pot: PoTEnum,
        league_id: int | None,
        patch_id: int | None,
        aggregation_type: int,
        calculation_type_id: int,
        game_stage: str,
        flat: Optional[bool],
):
    PQC = APIAggregationPerformanceQueryCreator()
    if flat is not None:
        select_query = PQC.get_aggregation_comparison_query(
            pot=pot,
            league_id=league_id,
            patch_id=patch_id,
            aggregation_type=aggregation_type,
            calculation_type_id=calculation_type_id,
            is_flat=flat,
        )
    else:
        select_query = PQC.get_aggregation_query(
            pot=pot,
            league_id=league_id,
            patch_id=patch_id,
            aggregation_type=aggregation_type,
            calculation_type_id=calculation_type_id,
        )
    model_names = PQC.get_model_names()

    query_output = await db_session.exec(select_query)

    data, value_mapping, has_total_field = process_db_output(
        query=query_output,
        model_names=model_names,
        game_stage=game_stage
    )

    return data, value_mapping, has_total_field, PQC.get_model_names(only_header=True)


def _update_variable(dict_: dict, key_: int | str, new_var: int | str):
    dict_.update({ key_: new_var })
    return dict_


def _order_ccomp_dict(dict_: dict, field: abc.Hashable) -> dict:
    return { k: v for k, v in sorted(dict_.items(), key=lambda item: str(item[1][field]).lower(), ) }


def _extract_ccomp_value(*values, field_name: str, is_total_data: bool) -> float | None:
    if is_total_data:
        return getattr(values[0], field_name)
    return extract_window_data_for_field(values[1], values[0], field_name)


async def get_cross_comparison_performance_data(
        db_session: AsyncSession,
        pot: PoTEnum,
        league_id: int | None,
        patch_id: int | None,
        aggregation_type: int,
        position: int,
        data_field: str,
        calculation_type_id: int,
        flat: bool,
):
    is_total_data = calculation_type_id == 0

    PQC = APICrossComparisonPerformanceQueryCreator()
    select_query = PQC.get_cross_comparison_query(
        pot=pot,
        league_id=league_id,
        patch_id=patch_id,
        aggregation_type_id=aggregation_type,
        position_id=position,
        data_field=data_field,
        calculation_type_id=calculation_type_id,
        is_flat=flat,
    )

    query_output = await db_session.exec(select_query)

    # REFORMATTED _processing_db_output
    TMMF = TableMinMaxFinder()
    output_dict = dict()
    rename_dict = dict()
    # hero/player name | id in db | id in db of the comparans player/hero
    for *performance_value, this_actor, this_actor_id, this_cps in query_output.all():
        value = _extract_ccomp_value(*performance_value, field_name=data_field, is_total_data=is_total_data)

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

        TMMF.add(column=this_cps, value=value)

    # LOOKING FOR DIFFERENCE VALUES
    ordered_names = sorted(rename_dict.values(), key=lambda x: (x).lower())
    # REMOVING OLD VALUES FROM DICTIONARY
    new_output = dict()
    for item_name, item in output_dict.items():
        temp_dict = dict()
        for id_, value in item.items():  # id / value
            cps_name = rename_dict.get(id_, id_)

            if cps_name != id_:
                TMMF.add_alias(id_, cps_name)

            temp_dict[cps_name] = value

        new_output[item_name] = {
            (o_name if o_name != item_name else aggregation_type):
                (
                    temp_dict.get(o_name, None)
                    if o_name != item_name else
                    temp_dict[aggregation_type]
                )
            for o_name in ordered_names
        }

    new_output = _order_ccomp_dict(new_output, aggregation_type)

    return new_output, TMMF.get_minmax_values(use_alias=True)
