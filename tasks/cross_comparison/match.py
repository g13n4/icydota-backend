from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session

from constants.calculation.game.calculation_types import WindowCalculations
from db import get_sync_db_session
from models import ComparisonType, League, CrossComparisonType
from models.performance import Performance
from modules.processors.totals import TotalPerformanceProcessor
from modules.processors.windows import WindowsPerformanceProcessor
from modules.query_creators.cross_comparison_query_creator_function import match_ccomparison_query_creator
from tasks.cross_comparison.helpers import CrossComparisonKeyCreator, COMPARISON_TYPE_POSITION_MAP
from tasks.helpers import process_data, get_query_data


logger = get_task_logger(__name__)


def create_performance_dict(
        league_id: int,
        data,
        CCKC: CrossComparisonKeyCreator,
        is_flat: bool,
        ccomparison_type: int,
        position_type: int,
        patch_id: int | None,
) -> dict[tuple, Performance]:
    performance_dict = dict()
    for item in data:
        key_tuple = CCKC.create_key(item, append=is_flat)
        key_dict = CCKC.create_dict(item)

        comparison_obj = ComparisonType(
            is_flat=is_flat,
            basic=False,
            **key_dict,
        )

        ccomparison_obj = CrossComparisonType(
            league_id=league_id,
            type_id=ccomparison_type,
            patch_id=patch_id,
            position_aggregation_id=position_type,
        )

        performance_obj = Performance(
            type_id=Performance.const.game.CROSS_COMPARISON,
            comparison_type=comparison_obj,
            cross_comparison_type=ccomparison_obj,
        )

        performance_dict[key_tuple] = performance_obj

    return performance_dict


# TODO: add patch_id functionality
@shared_task(name="cross_comparison_league_match", ignore_result=True)
def cross_comparison_league_match(league_id: int, ccomparison_type: int, patch_id: int | None = None):
    db_session: Session = get_sync_db_session(expire=False)

    league_obj = db_session.get(League, league_id)
    if not league_obj or not (league_id or patch_id):
        raise ValueError("No such league in the database")

    CCKC = CrossComparisonKeyCreator(ccomparison_type)
    columns = CCKC.get_fields()

    for ccomp_pos_id, enemies in COMPARISON_TYPE_POSITION_MAP.items():
        for is_flat in [True, False]:
            performance_dict = None
            for calculation in WindowCalculations.VALUES:

                query, names = match_ccomparison_query_creator(
                    league_id=league_id,
                    calculation_type_id=calculation.db_id,
                    positions=enemies,
                    is_flat=is_flat
                )
                data = get_query_data(db_session=db_session, query=query, names=names)

                if performance_dict is None:
                    performance_dict = create_performance_dict(
                        league_id=league_id,
                        data=data,
                        CCKC=CCKC,
                        is_flat=is_flat,
                        ccomparison_type=ccomparison_type,
                        position_type=ccomp_pos_id,
                        patch_id=patch_id,
                    )

                for window_data in process_data(data=data, group_by=columns, is_window=True):
                    PWD_obj = WindowsPerformanceProcessor.get_pwd_from_iterable(window_data, calculation.db_id)

                    performance_key = CCKC.create_key(window_data, append=is_flat)
                    performance_obj = performance_dict[performance_key]
                    PWD_obj.performance = performance_obj
                    db_session.add(PWD_obj)

                db_session.commit()

            query, names = match_ccomparison_query_creator(
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
