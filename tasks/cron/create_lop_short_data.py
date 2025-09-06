from collections import defaultdict

from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import text, select, Session

from constants.calculation.game.calculation_types import WindowCalculations
from db import get_sync_db_session
from models import Game, Patch
from models.league_and_patch_short_data import LoPShortData, LoPShortDataMomentum


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


def create_short_data_from_iterable(db_session: Session, field: str, field_id: int | str) -> dict:
    counter = 0
    data_dict = defaultdict(lambda: 0)
    for data_tuple in db_session.execute(text(QUERY.format(field, field_id))).all():
        for data_name, data_value in zip(FIELDS_SUM + FIELDS_AVG, data_tuple):
            if data_name.endswith("_win") or data_name.startswith("win_"):
                data_value = 1 if data_value else 0
            data_dict[data_name] += data_value
        counter += 1

    if counter == 0:
        raise ValueError

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
    return data_dict


@shared_task(name='create_short_data_patch_(cron)', ignore_result=True)
def create_short_data_for_patch_cron(patch_id: int) -> None:
    db_session: Session = get_sync_db_session(expire=True)

    logger.info(f"Processing patch for data table header")

    try:
        data_dict = create_short_data_from_iterable(
            db_session=db_session,
            field="patch_id",
            field_id=patch_id,
        )
    except (ValueError, ZeroDivisionError):
        logger.info(f"No appropriate data found")
        return None

    data_obj = db_session.exec(select(LoPShortData).where(LoPShortData.patch_id == patch_id)).first()
    if data_obj:
        logger.info(f"Data table header already exists... Updating data")
        data_obj.sqlmodel_update(data_dict)
    else:
        data_obj = LoPShortData(patch_id=patch_id, **data_dict)

    db_session.add(data_obj)
    db_session.full_commit()

    return None


@shared_task(name='create_short_data_league_(cron)', ignore_result=True)
def create_short_data_for_league_cron(league_id: int) -> None:
    db_session: Session = get_sync_db_session(expire=True)

    logger.info(f"Processing patch for data table header")

    field = "league_id"
    field_id = league_id

    try:
        league_data_dict = create_short_data_from_iterable(
            db_session=db_session,
            field=field,
            field_id=field_id,
        )
    except ValueError | ZeroDivisionError:
        logger.info(f"No appropriate data found")
        return None

    select_output = db_session.exec(
        select(LoPShortData, LoPShortDataMomentum)
        .join(LoPShortDataMomentum, LoPShortDataMomentum.data_id == LoPShortData.id, isouter=True)
        .where(LoPShortData.league_id == league_id)
    ).first()

    momentum_obj = None
    data_obj = None
    if select_output is not None:
        data_obj, momentum_obj = select_output

    if data_obj:
        logger.info(f"Data table header already exists... Updating data")
        data_obj.sqlmodel_update(league_data_dict)
    else:
        data_obj = LoPShortData(league_id=league_id, **league_data_dict)

    db_session.add(data_obj)

    patch_query = db_session.exec(select(Game.patch_id).where(Game.league_id == league_id).distinct())
    patch_ids = [x for x in patch_query.all()]
    patch_ids_len = len(patch_ids)

    patch_objs = db_session.exec(
        select(LoPShortData, Patch.name)
        .join(Patch, Patch.id == LoPShortData.patch_id)
        .where(
            (LoPShortData.patch_id).in_(patch_ids)
        ).distinct()
    )
    patch_names = []
    patch_dict = defaultdict(lambda: 0)
    for patch_obj, patch_name in patch_objs.all():
        for field in LoPShortData.const.VALUES:
            patch_dict[field.name] = getattr(patch_obj, field.name)

        patch_names.append(patch_name)

    if not patch_names:
        db_session.full_commit()
        return None

    patches_count = len(patch_names)
    if patches_count != patch_ids_len:
        data_obj.partial_comparison = True

    if momentum_obj is None:
        momentum_obj = LoPShortDataMomentum()

    for field in LoPShortData.const.VALUES:
        if field.is_comparable:
            setattr(
                momentum_obj,
                field.name,
                patch_dict[field.name] / patches_count
            )

    momentum_obj.compared_to = ", ".join(patch_names)

    data_obj.momentum = momentum_obj

    db_session.add(momentum_obj)
    db_session.add(data_obj)
    db_session.full_commit()

    return None
