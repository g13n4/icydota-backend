from celery import shared_task
from sqlmodel import Session

from constants.calculation.game.calculation_types import WindowCalculations
from db import get_sync_db_session
from models import ComparisonType, League, CrossComparisonType
from models.performance import Performance
from modules.processors.totals import TotalPerformanceProcessor
from modules.processors.windows import WindowsPerformanceProcessor
from modules.query_creators.cross_comparison_query_creator_function import ccomparison_query_creator
from tasks.cross_comparison.helpers import CrossComparisonKeyCreator, COMPARISON_TYPE_POSITION_MAP
from tasks.helpers import PROCESSING_COMPARISON_LIST, unpack_row, process_data


PROCESSING_ONLY_COMPARISON = PROCESSING_COMPARISON_LIST[1:]


def create_performance_obj(
        league_id: int,
        data,
        CCKC: CrossComparisonKeyCreator,
        is_flat: bool,
        ccomparison_type: int,
        position_type: int,
) -> Performance:
    key_dict = CCKC.create_dict(data)

    comparison_obj = ComparisonType(
        flat=is_flat,
        basic=False,
        **key_dict,
    )

    ccomparison_obj = CrossComparisonType(
        league_id=league_id,
        type_id=ccomparison_type,
        position_aggregation_id=position_type,
    )

    performance_obj = Performance(
        type_id=Performance.const.game.CROSS_COMPARISON,
        comparison_type=comparison_obj,
        cross_comparison_type=ccomparison_obj,
    )

    return performance_obj


def get_query_data(db_session, query, names: list[str]) -> list[dict]:
    query_output = db_session.exec(query)

    data = list()
    for row in query_output.all():
        row_data = unpack_row(row, names)
        data.append(row_data)

    return data


@shared_task(name="aggregate_league", ignore_result=True)
def aggregation_task(league_id: int, ccomparison_type: int):
    db_session: Session = get_sync_db_session(expire=False)

    league_obj = db_session.get(League, league_id)
    if not league_obj:
        raise ValueError("No such league in the database")

    CCKC = CrossComparisonKeyCreator(ccomparison_type)
    columns = CCKC.get_fields()

    for ccomp_pos_id, enemies in COMPARISON_TYPE_POSITION_MAP.items():
        for is_comparison, is_flat in PROCESSING_ONLY_COMPARISON:
            performance_obj = None

            for calculation in WindowCalculations.VALUES:
                query, names = ccomparison_query_creator(
                    league_id=league_id,
                    data_calculation_id=calculation.value,
                    positions=enemies,
                    is_flat=is_flat,
                )
                data = get_query_data(db_session=db_session, query=query, names=names)

                if performance_obj is None:
                    performance_obj = create_performance_obj(
                        league_id=league_id,
                        data=data,
                        CCKC=CCKC,
                        is_flat=is_flat,
                        ccomparison_type=ccomparison_type,
                        position_type=ccomp_pos_id,
                    )
                    db_session.add(performance_obj)

                for window_data in process_data(data=data, group_by=columns, is_window=True):
                    PWD_obj = WindowsPerformanceProcessor.get_pwd_from_iterable(window_data, calculation.value)
                    PWD_obj.game_performance = performance_obj
                    db_session.add(PWD_obj)

                db_session.commit()

            query, names = ccomparison_query_creator(
                league_id=league_id,
                data_calculation_id=None,
                positions=[],
                is_flat=is_flat, )
            data = get_query_data(db_session=db_session, query=query, names=names)

            for total_data in process_data(data=data, group_by=columns, is_window=False):
                PTD_obj = TotalPerformanceProcessor.create_object_from_dict(total_data)
                PTD_obj.game_performance = performance_obj
                db_session.add(PTD_obj)

            db_session.commit()
