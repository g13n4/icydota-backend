import pandas as pd
import numpy as np
from sqlalchemy.orm import aliased
from celery.utils.log import get_task_logger
from sqlmodel import Session, select, col
from celery import shared_task
from typing import Dict, List, Tuple

from sqlmodel import text

from db import get_sync_db_session
from models import ComparisonType, Hero, Player

logger = get_task_logger(__name__)


def set_names(pos_id: int, hero_name: str, player_name: str) -> Tuple[str, str]:
    return f'{pos_id}/{hero_name}', f'{pos_id}/{hero_name}/{player_name}'


@shared_task(name='set_comparison_names', ignore_result=True)
def set_comparison_names() -> None:
    logger.info('Filling names for comparison values')


    db_session: Session = get_sync_db_session()

    hero_cpd = aliased(Hero)
    player_cpd = aliased(Player)

    hero_cps = aliased(Hero)
    player_cps = aliased(Player)

    qr_output: [ComparisonType, str, str, str, str] = (
        db_session.exec(select(ComparisonType, hero_cpd.name, hero_cps.name,
                               player_cpd.nickname, player_cps.nickname)
                        .join(hero_cpd, onclause=hero_cpd.id == ComparisonType.hero_cpd_id)
                        .join(hero_cps, onclause=hero_cps.id == ComparisonType.hero_cps_id)
                        .join(player_cpd, onclause=player_cpd.account_id == ComparisonType.player_cpd_id)
                        .join(player_cps, onclause=player_cps.account_id == ComparisonType.player_cps_id)))


    for ct_obj, cpd_hero_name, cps_hero_name, cpd_player_name,  cps_player_name in qr_output.all():
        cpd_name_short, cpd_name = set_names(ct_obj.pos_cpd_id, cpd_hero_name, cpd_player_name)
        ct_obj.cpd_name_short = cpd_name_short
        ct_obj.cpd_name = cpd_name

        cps_name_short, cps_name = set_names(ct_obj.pos_cps_id, cps_hero_name, cps_player_name)
        ct_obj.cps_name_short = cps_name_short
        ct_obj.cps_name = cps_name

        db_session.add(ct_obj)

    db_session.commit()
    db_session.close()


logger.info(f"Comparison name values filled")

