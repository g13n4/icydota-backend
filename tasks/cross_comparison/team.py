from celery import shared_task

from constants.calculation.game.calculation_types import WindowCalculations
from models.performance import Performance
from models.performance_data_type import ByTeamType
from modules.processors.totals import TotalPerformanceProcessor
from modules.processors.windows import WindowsPerformanceProcessor
from modules.query_creators.cross_comparison_query_creator_function import (
    team_ccomparison_query_creator,
)
from tasks.helpers import process_data, get_query_data
from tasks.task_decorator import processing_task_decorator


def _get_key(data: dict, is_flat: bool | None) -> tuple[int, int, bool | None]:
    return (data['team_cpd_id'], data['team_cps_id'], is_flat)


def create_performance_dict(
        league_id: int | None,
        data,
        is_flat: bool,
        patch_id: int | None,
) -> dict[tuple, Performance]:
    output = dict()
    for item in data:
        key = _get_key(item, is_flat)

        type_obj = ByTeamType(
            patch_id=patch_id,
            league_id=league_id,
            team_id=item['team_cpd_id'],
            is_flat=is_flat,
            team_cpd_id=item['team_cpd_id'],
            team_cps_id=item['team_cps_id'],
        )

        performance_obj = Performance(
            type_id=Performance.const.team.TEAM_MATCH_CROSS_COMPARISON,
            by_team_type=type_obj,
        )
        output[key] = performance_obj

    return output


@shared_task(name="cross_comparison_league_team", ignore_result=True)
@processing_task_decorator
def cross_comparison_league_team(db_session, league_id: int, patch_id: int | None = None):
    columns = ['team_cpd_id', 'team_cps_id']

    for is_flat in [True, False]:
        performance_dict = None
        for calculation in WindowCalculations.VALUES:
            query, names = team_ccomparison_query_creator(
                league_id=league_id,
                patch_id=patch_id,
                calculation_type_id=calculation.db_id,
                is_flat=is_flat
            )
            data = get_query_data(db_session=db_session, query=query, names=names)

            if performance_dict is None:
                performance_dict = create_performance_dict(
                    league_id=league_id,
                    data=data,
                    is_flat=is_flat,
                    patch_id=patch_id,
                )

            for window_data in process_data(data=data, group_by=columns, is_window=True):
                PWD_obj = WindowsPerformanceProcessor.get_pwd_from_iterable(window_data, calculation.db_id)
                key = _get_key(window_data, is_flat)
                performance_obj = performance_dict[key]

                PWD_obj.performance = performance_obj
                db_session.add(PWD_obj)

            db_session.commit()

        query, names = team_ccomparison_query_creator(
            league_id=league_id,
            patch_id=patch_id,
            calculation_type_id=None,
            is_flat=is_flat
        )
        data = get_query_data(db_session=db_session, query=query, names=names)

        for total_data in process_data(data=data, group_by=columns, is_window=False):
            PTD_obj = TotalPerformanceProcessor.create_object_from_dict(total_data)
            key = _get_key(total_data, is_flat)
            performance_obj = performance_dict[key]
            PTD_obj.performance = performance_obj
            db_session.add(PTD_obj)

        db_session.commit()
