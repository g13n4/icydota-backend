from celery import shared_task

from constants.calculation.game.calculation_types import WindowCalculations
from modules.key_creators.ccomparison_key_creator import CrossComparisonTeamKeyCreator
from modules.processors.totals import TotalPerformanceProcessor
from modules.processors.windows import WindowsPerformanceProcessor
from modules.query_creators.cross_comparison_query_creator_function import (
    team_ccomparison_query_creator,
)
from tasks.helpers import process_data, get_query_data
from tasks.task_decorator import validate_league_and_patch
from tasks.utils.performance_object_creation.team_cross_comparison_objects import \
    create_team_cross_comparison_performance_objs


@shared_task(name="cross_compare_team", ignore_result=True)
@validate_league_and_patch
def cross_compare_team_task(db_session, league_id: int, patch_id: int | None = None):
    CCTKC = CrossComparisonTeamKeyCreator()

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
                performance_dict = create_team_cross_comparison_performance_objs(
                    db_session=db_session,
                    league_id=league_id,
                    patch_id=patch_id,
                    data=data,
                    is_flat=is_flat,
                    KC=CCTKC,
                )

            for window_data in process_data(data=data, group_by=CCTKC.fields, is_window=True):
                PWD_obj = WindowsPerformanceProcessor.get_pwd_from_iterable(window_data, calculation.db_id)
                key = CCTKC.create_key(window_data, append=is_flat)
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

        for total_data in process_data(data=data, group_by=CCTKC.fields, is_window=False):
            PTD_obj = TotalPerformanceProcessor.create_object_from_dict(total_data)
            key = CCTKC.create_key(total_data, append=is_flat)
            performance_obj = performance_dict[key]
            PTD_obj.performance = performance_obj
            db_session.add(PTD_obj)

        db_session.commit()
