from typing import Callable

from celery import shared_task

from modules.processors.totals import TotalPerformanceProcessor
from modules.processors.windows import WindowsPerformanceProcessor
from tasks.helpers import process_data, get_query_data
from tasks.parallel.decorators import parallel_processing_task_decorator


@shared_task(name="one_calculation_aggregate_player", ignore_result=True)
@parallel_processing_task_decorator
def process_one_calculation_aggregate_player_task(
        db_session,
        CK,
        performance_map: dict,
        calculation_id: int,
        query_func: Callable,
        league_id: int | None = None,
        patch_id: int | None = None,
        is_comparison: bool | None = None,
        is_flat: bool | None = None,
        **kwargs,
):
    columns = CK.get_fields()

    is_window = bool(calculation_id)

    query, names = query_func(
        league_id=league_id,
        patch_id=patch_id,
        calculation_type_id=calculation_id,
        is_comparison=is_comparison,
        is_flat=is_flat,
        **kwargs,
    )
    data = get_query_data(db_session=db_session, query=query, names=names)

    for processed_data in process_data(data=data, group_by=columns, is_window=is_window):
        key = CK.create_key(processed_data, append=is_flat)
        if is_window:
            obj = WindowsPerformanceProcessor.get_pwd_from_iterable(processed_data, calculation_id)
            obj.performance_id = performance_map[key]
        else:
            obj = TotalPerformanceProcessor.create_object_from_dict(processed_data)
            obj.performance_id = performance_map[key]
        db_session.add(obj)

    db_session.commit()
