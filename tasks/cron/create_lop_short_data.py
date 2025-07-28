from collections import defaultdict

from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import text, Session, select

from constants.calculation.game.calculation_types import WindowCalculations
from db import get_sync_db_session
from models.league_and_patch_short_data import LoPShortDataData


logger = get_task_logger(__name__)

FIELDS_SUM = ["first_pick_win", "last_pick_win", "win_sent", "win_dire", "net_worth", "hero_kills", "last_hits"]
FIELDS_AVG = ["duration"]
FIELDS_STR = "".join(
    [
        ",".join(map(lambda field: f"SUM(ptd.{field})", FIELDS_SUM)),
        ",",
        ",".join(map(lambda field: f"AVG(ptd.{field})", FIELDS_AVG))
    ]
)
QUERY = f"select {FIELDS_STR} " + \
        """
        from performances p
        JOIN by_team_types btt  ON p.id = btt.performance_id AND btt.match_id is not null
        JOIN performance_totals_data ptd  ON ptd.performance_id = p.id
        WHERE btt.{0} = {1} AND p.type_id = 201   
        GROUP BY btt.match_id
        """

QUERY_AT_15 = """
select pgd.position_id, AVG(ptd.g15)
from games g
JOIN players_game_data pgd  ON pgd.game_id = g.id
JOIN performances p  ON pgd.id = p.player_game_data_id  AND p.type_id = 101
JOIN performance_windows_data pwd  ON pwd.performance_id = p.id AND pwd.calc_type_id = {2}
JOIN performance_windows_table ptd  ON ptd.id = pwd.performance_table_id
WHERE g.{0} = {1}
GROUP BY pgd.position_id
"""


@shared_task(name='create_short_data_for_league_and_patch_(cron)', ignore_result=True)
def create_short_data_for_league_and_patch_cron(
        league_id: int | None = None,
        patch_id: int | None = None,
) -> None:
    db_session: Session = get_sync_db_session(expire=True)


    if league_id:
        logger.info(f"Processing league for data table header")

        field = "league_id"
        field_id = league_id
        where = LoPShortDataData.league_id == league_id
    elif patch_id:
        logger.info(f"Processing patch for data table header")

        field = "patch_id"
        field_id = patch_id
        where = LoPShortDataData.patch_id == patch_id
    else:
        raise TypeError("No argument provided")

    counter = 0
    data_dict = defaultdict(lambda: 0)
    for data_tuple in db_session.execute(text(QUERY.format(field, field_id))).all():
        for data_name, data_value in zip(FIELDS_SUM + FIELDS_AVG, data_tuple):
            if data_name.endswith("_win") or data_name.startswith("win_"):
                data_value = 1 if data_value else 0
            data_dict[data_name] += data_value
        counter += 1

    kpm = data_dict["hero_kills"] / ((data_dict["duration"] + 90) // 60)
    data_dict = { name: value / counter for name, value in data_dict.items() }
    data_dict["matches"] = counter
    data_dict["kpm"] = kpm

    for data_calc in [WindowCalculations.networth__max, WindowCalculations.xp__lvl]:
        for data_tuple in db_session.execute(text(QUERY_AT_15.format(field, field_id, data_calc.db_id))).all():
            position, value = data_tuple

            if position in [1, 2, 3]:
                start_name = "cores"
            else:
                start_name = "supports"

            if data_calc == WindowCalculations.networth__max:
                mid_name = "networth"
            else:
                mid_name = "level"

            data_dict[f"{start_name}_{mid_name}_at_15"] = value

    params = { field: field_id }
    data_obj = db_session.exec(select(LoPShortDataData).where(where)).first()
    if data_obj:
        logger.info(f"Data table header already exists... Updating data")
        data_obj.sqlmodel_update(data_dict)
    else:
        data_obj = LoPShortDataData(
            **params,
            **data_dict,
        )

    db_session.add(data_obj)
    db_session.full_commit()
