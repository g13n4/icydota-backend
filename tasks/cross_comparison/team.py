from celery import shared_task
from sqlmodel import Session

from constants.calculation.game.calculation_types import WindowCalculations
from db import get_sync_db_session
from models import ComparisonType, League, CrossComparisonType
from models.performance import Performance
from models.performance_data_type import ByTeamType
from modules.processors.totals import TotalPerformanceProcessor
from modules.processors.windows import WindowsPerformanceProcessor
from modules.query_creators.cross_comparison_query_creator_function import match_ccomparison_query_creator, \
    team_ccomparison_query_creator
from tasks.cross_comparison.helpers import CrossComparisonKeyCreator, COMPARISON_TYPE_POSITION_MAP
from tasks.helpers import PROCESSING_COMPARISON_LIST, unpack_row, process_data, get_query_data


PROCESSING_ONLY_COMPARISON = PROCESSING_COMPARISON_LIST[1:]


def _get_key(data: dict, is_flat: bool | None) -> tuple[int, int, bool | None]:
    return (data['team_cpd_id'], data['team_cps_id'], is_flat)


def create_performance_dict(
        league_id: int,
        data,
        is_flat: bool,
) -> tuple[int, dict[tuple, Performance]]:
    patch_id = 0
    output = dict()
    for item in data:
        key = _get_key(item, is_flat)
        patch_id = max(item[patch_id], patch_id)

        type_obj = ByTeamType(
            patch_id=None,  # either aggregate or choose one
            league_id=league_id,
            team_id=item['team_id'],
            is_flat=is_flat,
            team_cpd_id=item['team_cpd_id'],
            team_cps_id=item['team_cps_id'],
        )

        performance_obj = Performance(
            type_id=Performance.const.team.TEAM_MATCH_CROSS_COMPARISON,
            by_team_type=type_obj,
        )
        output[key] = performance_obj

    return patch_id, output



@shared_task(name="cross_comparison_league_team", ignore_result=True)
def aggregation_task(league_id: int):
    db_session: Session = get_sync_db_session(expire=False)

    league_obj = db_session.get(League, league_id)
    if not league_obj:
        raise ValueError("No such league in the database")

    columns = ['team_id']
    performance_dict = None
    patch_id = None

    for ccomp_pos_id, enemies in COMPARISON_TYPE_POSITION_MAP.items():
        for is_comparison, is_flat in PROCESSING_ONLY_COMPARISON:
            for calculation in WindowCalculations.VALUES:
                query, names = team_ccomparison_query_creator(
                    league_id=league_id,
                    data_calculation_id=calculation.value,
                    positions=enemies,
                    is_flat=is_flat
                    )
                data = get_query_data(db_session=db_session, query=query, names=names)

                if performance_dict is None:
                    patch_id, performance_dict = create_performance_dict(
                        league_id=league_id,
                        data=data,
                        is_flat=is_flat,
                    )

                for window_data in process_data(data=data, group_by=columns, is_window=True):
                    PWD_obj = WindowsPerformanceProcessor.get_pwd_from_iterable(window_data, calculation.value)
                    key = _get_key(window_data, is_flat)
                    performance_obj = performance_dict[key]
                    performance_obj.patch_id = patch_id

                    PWD_obj.game_performance = performance_obj
                    db_session.add(PWD_obj)

                db_session.commit()

            query, names = match_ccomparison_query_creator(
                league_id=league_id,
                data_calculation_id=None,
                positions=[],
                is_flat=is_flat
                )
            data = get_query_data(db_session=db_session, query=query, names=names)

            for total_data in process_data(data=data, group_by=columns, is_window=False):
                PTD_obj = TotalPerformanceProcessor.create_object_from_dict(total_data)
                key = _get_key(total_data, is_flat)
                performance_obj = performance_dict[key]
                PTD_obj.game_performance = performance_obj
                db_session.add(PTD_obj)

            db_session.commit()
