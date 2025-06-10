from celery import shared_task

from modules.processors.totals import TotalPerformanceProcessor
from modules.processors.windows import WindowsPerformanceProcessor
from modules.query_creators.match_aggregation_query_creator_function import match_aggregation_query_creator
from tasks.aggregation.helpers import AggregationKeyCreator
from tasks.helpers import process_data, get_query_data
from tasks.task_decorator import parallel_processing_task_decorator


@shared_task(name="one_calculation_aggregate_player", ignore_result=True)
@parallel_processing_task_decorator("aggregation", "player")
def process_one_calculation_aggregate_player_task(
        db_session,
        AGC: AggregationKeyCreator,
        performance_map: dict,
        calculation_id: int,
        league_id: int | None = None,
        patch_id: int | None = None,
        is_comparison: bool | None = None,
        is_flat: bool | None = None,
        **kwargs,
):
    columns = AGC.get_fields()

    if calculation_id:
        query, names = match_aggregation_query_creator(
            league_id=league_id,
            patch_id=patch_id,
            calculation_type_id=calculation_id,
            is_comparison=is_comparison,
            is_flat=is_flat
        )
        data = get_query_data(db_session=db_session, query=query, names=names)

        for window_data in process_data(data=data, group_by=columns, is_window=True):
            key = AGC.create_key(window_data, append=is_flat)
            PWD_obj = WindowsPerformanceProcessor.get_pwd_from_iterable(window_data, calculation_id)
            PWD_obj.performance_id = performance_map[key]
            db_session.add(PWD_obj)

    else:
        query, names = match_aggregation_query_creator(
            league_id=league_id,
            patch_id=patch_id,
            calculation_type_id=None,
            is_comparison=is_comparison,
            is_flat=is_flat,
        )
        data = get_query_data(db_session=db_session, query=query, names=names)

        for total_data in process_data(data=data, group_by=columns, is_window=False):
            key = AGC.create_key(total_data, append=is_flat)
            PTD_obj = TotalPerformanceProcessor.create_object_from_dict(total_data)
            PTD_obj.performance_id = performance_map[key]
            db_session.add(PTD_obj)

    db_session.commit()
