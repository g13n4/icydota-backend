from celery import shared_task

from constants.calculation.game.calculation_types import WindowCalculations
from modules.key_creators.aggregation_key_creator import AggregationPlayerKeyCreator
from modules.processors.totals import TotalPerformanceProcessor
from modules.processors.windows import WindowsPerformanceProcessor
from modules.query_creators.match_aggregation_query_creator_function import match_aggregation_query_creator
from tasks.helpers import PROCESSING_COMPARISON_LIST, process_data, get_query_data
from tasks.task_decorator import processing_task_decorator
from tasks.utils.performance_object_creation.player_aggregation_objects import \
    create_player_aggregation_performance_objs


@shared_task(name="aggregate_league_player", ignore_result=True)
@processing_task_decorator
def aggregate_league_player_task(
        db_session,
        aggregation_type: int,
        league_id: int | None = None,
        patch_id: int | None = None
):
    AGC = AggregationPlayerKeyCreator(aggregation_type)
    columns = AGC.get_fields()

    performance_dict = create_player_aggregation_performance_objs(
        db_session=db_session,
        league_id=league_id,
        patch_id=patch_id,
        AGC=AGC,
    )

    for is_comparison, is_flat in PROCESSING_COMPARISON_LIST:
        for calculation in WindowCalculations.VALUES:
            query, names = match_aggregation_query_creator(
                league_id=league_id,
                patch_id=patch_id,
                calculation_type_id=calculation.db_id,
                is_comparison=is_comparison,
                is_flat=is_flat
            )
            data = get_query_data(db_session=db_session, query=query, names=names)

            for window_data in process_data(data=data, group_by=columns, is_window=True):
                key = AGC.create_key(window_data, append=is_flat)
                PWD_obj = WindowsPerformanceProcessor.get_pwd_from_iterable(window_data, calculation.db_id)
                PWD_obj.performance = performance_dict[key]
                db_session.add(PWD_obj)

            db_session.commit()

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
            PTD_obj.performance = performance_dict[key]
            db_session.add(PTD_obj)

        db_session.commit()
