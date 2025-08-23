from sqlmodel.ext.asyncio.session import AsyncSession

from api.table.helpers import process_db_output
from constants.api import PoTEnum
from constants.performance.window import WINDOWS_BY_FIELD
from modules.ccomparion_header_creator import CrossComparisonProcessor
from modules.empty_mask_converter import EmptyMaskConverter
from modules.minmax_finder import TableMinMaxFinder
from modules.query_creators.performance.aggregation_performance_query_creator import \
    APIAggregationPerformanceQueryCreator
from modules.query_creators.performance.crosscomparison_performance_query_creator import \
    APICrossComparisonPerformanceQueryCreator
from modules.query_creators.performance.match_performance_query_creator import APIMatchPerformanceQueryCreator


async def get_performance_data(
        db_session: AsyncSession,
        pot: PoTEnum,
        match_id: int,
        data_type: int,
        game_stage: str | None,
):
    PQC = APIMatchPerformanceQueryCreator()
    select_query = PQC.get_query(match_id=match_id, calculation_type_id=data_type, pot=pot)
    model_names = PQC.get_model_names()
    query_output = await db_session.exec(select_query)

    data, value_mapping, has_total_field = process_db_output(
        query=query_output,
        model_names=model_names,
        game_stage=game_stage,
        pot=pot,
        req_type="match",
        data_model_name=PQC.data_model_name,
        is_comparison=False,
    )

    return data, value_mapping, has_total_field, PQC.get_model_names(only_header=True)


async def get_performance_data_comparison(
        db_session: AsyncSession,
        pot: PoTEnum,
        match_id: int,
        calculation_type_id: int,
        game_stage: str | None,
        basic: bool,
        flat: bool | None,
):
    PQC = APIMatchPerformanceQueryCreator()
    select_query = PQC.get_comparison_query(
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
        is_comparison=True,
    )

    return data, value_mapping, has_total_field, PQC.get_model_names(only_header=True)


async def get_aggregated_performance_data(
        db_session: AsyncSession,
        pot: PoTEnum,
        league_id: int | None,
        patch_id: int | None,
        aggregation_type: int,
        calculation_type_id: int,
        game_stage: str | None = None,
        flat: bool | None = None,
):
    PQC = APIAggregationPerformanceQueryCreator()
    if flat is not None:
        select_query = PQC.get_comparison_query(
            pot=pot,
            patch_id=patch_id,
            league_id=league_id,
            aggregation_type=aggregation_type,
            calculation_type_id=calculation_type_id,
            is_flat=flat,
        )
    else:
        select_query = PQC.get_query(
            league_id=league_id,
            pot=pot,
            patch_id=patch_id,
            aggregation_type=aggregation_type,
            calculation_type_id=calculation_type_id,
        )

    model_names = PQC.get_model_names()
    query_output = await db_session.exec(select_query)
    data, value_mapping, has_total_field = process_db_output(
        query=query_output,
        model_names=model_names,
        game_stage=game_stage,
        pot=pot,
        req_type="aggregation",
        data_model_name=PQC.data_model_name,
        is_comparison=not (flat is None),
    )

    return data, value_mapping, has_total_field, PQC.get_model_names(only_header=True)


async def get_cross_comparison_performance_data(
        db_session: AsyncSession,
        pot: PoTEnum,
        league_id: int | None,
        patch_id: int | None,
        aggregation_type: int | None,
        position: int,
        data_field: str,
        calculation_type_id: int | None,
        flat: bool,
):
    PQC = APICrossComparisonPerformanceQueryCreator()
    select_query = PQC.get_comparison_query(
        pot=pot,
        league_id=league_id,
        patch_id=patch_id,
        type_id=aggregation_type,
        position_id=position,
        data_field=data_field,
        calculation_type_id=calculation_type_id,
        is_flat=flat
    )
    query_output = await db_session.exec(select_query)
    is_total = not bool(calculation_type_id)
    TMMF = TableMinMaxFinder()
    CCP = CrossComparisonProcessor(aggregation_type, TMMF, PQC.models.get_names()[1:])
    # hero/player name | id in db | id in db of the comparans player/hero
    data = { }
    if is_total:
        for value, *info in query_output.all():
            key, inner_key = CCP.process_data_row(*info)
            if key not in data:
                data[key] = { inner_key: value }
            else:
                data[key][inner_key] = value
    else:
        field_index = WINDOWS_BY_FIELD[data_field].order
        for value, mask_value, *info in query_output.all():
            if mask_value:
                value = EmptyMaskConverter.extract_from_mask(mask=mask_value, index=field_index)

            key, inner_key = CCP.process_data_row(*info)
            if key not in data:
                data[key] = { inner_key: value }
            else:
                data[key][inner_key] = value

    ordered_headers, sorted_data = CCP.rearrange_dict(data)
    return sorted_data, CCP.name, ordered_headers, CCP.TMMF.get_minmax_values(use_alias=True)
