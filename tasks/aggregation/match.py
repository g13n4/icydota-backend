from constants.calculation.game.calculation_types import WindowCalculations
from db import get_sync_db_session
from models import AggregationType, ComparisonType, League
from models.performance import Performance
from modules.processors.totals import TotalPerformanceProcessor
from modules.processors.windows import WindowsPerformanceProcessor
from modules.query_creators.match_aggregation_query_creator_function import match_aggregation_query_creator
from tasks.aggregation.helpers import AggregationKeyCreator, COMPARISON_MAP, match_aggregation_league_participants_query_creator
from sqlmodel import Session
from celery import shared_task

from tasks.helpers import PROCESSING_COMPARISON_LIST, unpack_row, process_data, get_query_data


def create_performance_objs(
        db_session,
        league_id: int,
        AGC: AggregationKeyCreator,
        ) -> dict[tuple, Performance]:
    output = dict()
    query, names = match_aggregation_league_participants_query_creator(league_id=league_id)
    league_participants = db_session.exec(query)

    for row in league_participants:
        row_data = { name: value for name, value in zip(row, names) }
        required_row_data = AGC.create_dict(row_data)

        for is_comparison, is_flat in PROCESSING_COMPARISON_LIST:
            row_key = AGC.create_key(row_data, append=is_flat)

            aggregation_obj = AggregationType(
                type_id=AGC.type_id,
                **required_row_data,
            )

            comparison_obj = None
            if is_comparison:
                comparison_data = { COMPARISON_MAP[name].cpd: value for name, value in required_row_data.items() }

                comparison_obj = ComparisonType(
                    is_flat=is_flat,
                    basic=False,
                    **comparison_data,
                )

            performance_type = Performance.const.game.AGGREGATION_COMPARISON if is_comparison \
                else Performance.const.game.AGGREGATION

            performance_obj = Performance(
                type_id=performance_type,
                aggregation_type=aggregation_obj,
                comparison_type=comparison_obj,
            )
            output[row_key] = performance_obj

            db_session.add(performance_obj)

    return output


@shared_task(name="aggregate_league_match", ignore_result=True)
def aggregate_league_match(league_id: int, aggregation_type: int):
    db_session: Session = get_sync_db_session(expire=False)

    league_obj = db_session.get(League, league_id)
    if not league_obj:
        raise ValueError("No such league in the database")

    AGC = AggregationKeyCreator(aggregation_type)
    columns = AGC.get_fields()

    performance_dict = create_performance_objs(db_session=db_session, league_id=league_id, AGC=AGC)

    for is_comparison, is_flat in PROCESSING_COMPARISON_LIST:
        for calculation in WindowCalculations.VALUES:
            query, names = match_aggregation_query_creator(
                league_id=league_id,
                calculation_type_id=calculation.value_db,
                is_comparison=is_comparison,
                is_flat=is_flat
                )
            data = get_query_data(db_session=db_session, query=query, names=names)

            for window_data in process_data(data=data, group_by=columns, is_window=True):
                key = AGC.create_key(window_data, append=is_flat)
                PWD_obj = WindowsPerformanceProcessor.get_pwd_from_iterable(window_data, calculation.value)
                PWD_obj.game_performance = performance_dict[key]
                db_session.add(PWD_obj)

            db_session.commit()

        query, names = match_aggregation_query_creator(
            league_id=league_id,
            calculation_type_id=None,
            is_comparison=is_comparison,
            is_flat=is_flat
            )
        data = get_query_data(db_session=db_session, query=query, names=names)

        for total_data in process_data(data=data, group_by=columns, is_window=False):
            key = AGC.create_key(total_data, append=is_flat)
            PTD_obj = TotalPerformanceProcessor.create_object_from_dict(total_data)
            PTD_obj.game_performance = performance_dict[key]
            db_session.add(PTD_obj)

        db_session.commit()
