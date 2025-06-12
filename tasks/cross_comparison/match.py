from celery import shared_task

from constants.calculation.game.calculation_types import WindowCalculations
from modules.key_creators.ccomparison_key_creator import CrossComparisonPlayerKeyCreator
from modules.processors.totals import TotalPerformanceProcessor
from modules.processors.windows import WindowsPerformanceProcessor
from modules.query_creators.cross_comparison_query_creator_function import match_ccomparison_query_creator
from tasks.cross_comparison.helpers import COMPARISON_TYPE_POSITION_MAP
from tasks.helpers import process_data, get_query_data
from tasks.task_decorator import processing_task_decorator
from tasks.utils.performance_object_creation.player_cross_comparison_objects import \
    create_player_cross_comparison_performance_objs


@shared_task(name="cross_compare_player", ignore_result=True)
@processing_task_decorator
def cross_compare_player_task(db_session, league_id: int | None, patch_id: int | None, ccomparison_type: int):
    CCKC = CrossComparisonPlayerKeyCreator(ccomparison_type)
    columns = CCKC.get_fields()

    for ccomp_pos_id, enemies in COMPARISON_TYPE_POSITION_MAP.items():
        for is_flat in [True, False]:
            performance_dict = None
            for calculation in WindowCalculations.VALUES:

                query, names = match_ccomparison_query_creator(
                    patch_id=patch_id,
                    league_id=league_id,
                    calculation_type_id=calculation.db_id,
                    positions=enemies,
                    is_flat=is_flat
                )
                data = get_query_data(db_session=db_session, query=query, names=names)

                if performance_dict is None:
                    performance_dict = create_player_cross_comparison_performance_objs(
                        league_id=league_id,
                        patch_id=patch_id,
                        data=data,
                        CCKC=CCKC,
                        is_flat=is_flat,
                        ccomparison_type=ccomparison_type,
                        position_type=ccomp_pos_id,
                    )

                for window_data in process_data(data=data, group_by=columns, is_window=True):
                    PWD_obj = WindowsPerformanceProcessor.get_pwd_from_iterable(window_data, calculation.db_id)

                    performance_key = CCKC.create_key(window_data, append=is_flat)
                    performance_obj = performance_dict[performance_key]
                    PWD_obj.performance = performance_obj
                    db_session.add(PWD_obj)

                db_session.commit()

            query, names = match_ccomparison_query_creator(
                patch_id=patch_id,
                league_id=league_id,
                calculation_type_id=None,
                positions=enemies,
                is_flat=is_flat
            )
            data = get_query_data(db_session=db_session, query=query, names=names)

            for total_data in process_data(data=data, group_by=columns, is_window=False):
                PTD_obj = TotalPerformanceProcessor.create_object_from_dict(total_data)

                performance_key = CCKC.create_key(total_data, append=is_flat)
                performance_obj = performance_dict[performance_key]
                PTD_obj.performance = performance_obj
                db_session.add(PTD_obj)

            db_session.commit()
