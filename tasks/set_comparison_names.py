from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session, text

from constants.game_performance import GamePerformanceTypeConstant
from db import get_sync_db_session


logger = get_task_logger(__name__)


def get_sql_req(league_id: int | None = None) -> str:
    return ("""
            UPDATE comparison_types c_main
            SET cpd_name_short=CONCAT(pos_cpd.name, '/', h_cpd.name),
                cps_name_short=CONCAT(pos_cps.name, '/', h_cps.name),
                cpd_name=CONCAT(pos_cpd.name, '/', h_cpd.name, '/', p_cpd.nickname),
                cps_name=CONCAT(pos_cps.name, '/', h_cps.name, '/', p_cps.nickname)
            FROM comparison_types comp_data
            INNER JOIN performances p ON comp_data.performance_id = p.id
            INNER JOIN players_game_data pgd ON pgd.id = p.player_game_data_id
            INNER JOIN games g ON g.id = pgd.game_id
            INNER JOIN heroes h_cpd ON comp_data.hero_cpd_id = h_cpd.id
            INNER JOIN heroes h_cps ON comp_data.hero_cps_id = h_cps.id
            INNER JOIN players p_cpd ON comp_data.player_cpd_id = p_cpd.account_id
            INNER JOIN players p_cps ON comp_data.player_cps_id = p_cps.account_id
            INNER JOIN positions pos_cpd ON comp_data.pos_cpd_id = pos_cpd.id
            INNER JOIN positions pos_cps ON comp_data.pos_cps_id = pos_cpd.id
            """ +
            f"WHERE p.type_id = {GamePerformanceTypeConstant.MATCH_DATA_COMPARISON} " +
            "AND c_main.cpd_name_short is null " +
            "AND c_main.cps_name_short is null " +
            "AND c_main.cpd_name is null "
            "AND c_main.cps_name is null " +
            f"AND g.league_id = {league_id} " if league_id else ""
            )


@shared_task(name='set_comparison_names', ignore_result=True)
def set_comparison_names(league_id: None | int = None) -> None:
    logger.info('Filling names for comparison values')

    db_session: Session = get_sync_db_session(expire=True)

    sql_req = get_sql_req(league_id=league_id)
    db_session.execute(text(sql_req))

    db_session.full_commit()
    logger.info(f"Comparison name values filled")
