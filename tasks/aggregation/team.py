from celery import shared_task

from constants.calculation.game.calculation_types import WindowCalculations
from models.performance import Performance
from models.performance_data_type import ByTeamType
from modules.processors.totals import TotalPerformanceProcessor
from modules.processors.windows import WindowsPerformanceProcessor
from modules.query_creators.team_aggregation_query_creator_function import team_aggregation_query_creator
from tasks.aggregation.helpers import team_aggregation_league_participants_query_creator
from tasks.helpers import PROCESSING_COMPARISON_LIST, process_data, get_query_data
from tasks.task_decorator import processing_task_decorator


def _get_key(data: dict, is_flat: bool | None) -> tuple[int, bool | None]:
    return (data['team_id'], is_flat)


def create_performance_objs(
        db_session,
        league_id: int | None,
        patch_id: int | None,
) -> dict[tuple, Performance]:
    output = dict()
    query, names = team_aggregation_league_participants_query_creator(league_id=league_id, patch_id=patch_id)
    league_participants = db_session.exec(query)

    for row in league_participants:
        row_data = { name: value for name, value in zip(names, row) }

        for is_comparison, is_flat in PROCESSING_COMPARISON_LIST:
            row_key = _get_key(row_data, is_flat)

            type_obj = ByTeamType(
                patch_id=patch_id,  # either aggregate or choose one
                league_id=league_id,
                team_id=row_data['team_id'],
                is_flat=is_flat,
            )

            performance_type = Performance.const.team.TEAM_MATCH_AGGREGATION_COMPARISON if is_comparison \
                else Performance.const.team.TEAM_MATCH_AGGREGATION

            performance_obj = Performance(
                type_id=performance_type,
                by_team_type=type_obj,
            )
            output[row_key] = performance_obj

            db_session.add(performance_obj)

    return output


@shared_task(name="aggregate_league_team", ignore_result=True)
@processing_task_decorator
def aggregate_league_team_task(db_session, league_id: int | None = None, patch_id: int | None = None):
    columns = ['team_id']

    performance_dict = create_performance_objs(db_session=db_session, league_id=league_id, patch_id=patch_id)

    for is_comparison, is_flat in PROCESSING_COMPARISON_LIST:
        for calculation in WindowCalculations.VALUES:
            query, names = team_aggregation_query_creator(
                patch_id=patch_id,
                league_id=league_id,
                calculation_type_id=calculation.db_id,
                is_comparison=is_comparison,
                is_flat=is_flat,
            )
            data = get_query_data(db_session=db_session, query=query, names=names)

            for window_data in process_data(data=data, group_by=columns, is_window=True):
                key = _get_key(window_data, is_flat)
                PWD_obj = WindowsPerformanceProcessor.get_pwd_from_iterable(window_data, calculation.db_id)
                PWD_obj.performance = performance_dict[key]
                db_session.add(PWD_obj)

            db_session.commit()

        query, names = team_aggregation_query_creator(
            patch_id=patch_id,
            league_id=league_id,
            calculation_type_id=None,
            is_comparison=is_comparison,
            is_flat=is_flat
        )
        data = get_query_data(db_session=db_session, query=query, names=names)

        for total_data in process_data(data=data, group_by=columns, is_window=False):
            key = _get_key(total_data, is_flat)
            PTD_obj = TotalPerformanceProcessor.create_object_from_dict(total_data)
            PTD_obj.performance = performance_dict[key]
            db_session.add(PTD_obj)

        db_session.commit()
