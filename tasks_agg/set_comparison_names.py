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

    db_session.execute(
        text("""
UPDATE comparison_types c_main
SET cpd_name_short=CONCAT(comp_data.pos_cpd_id, '/', h_cpd.name),
    cps_name_short=CONCAT(comp_data.pos_cps_id, '/', h_cps.name),
    cpd_name=CONCAT(comp_data.pos_cpd_id, '/', h_cpd.name, '/', p_cpd.nickname),
    cps_name=CONCAT(comp_data.pos_cps_id, '/', h_cps.name, '/', p_cps.nickname)
FROM comparison_types comp_data
INNER JOIN heroes h_cpd ON comp_data.hero_cpd_id = h_cpd.id
INNER JOIN heroes h_cps ON comp_data.hero_cps_id = h_cps.id
INNER JOIN players p_cpd ON comp_data.player_cpd_id = p_cpd.account_id
INNER JOIN players p_cps ON comp_data.player_cps_id = p_cps.account_id
WHERE c_main.hero_cps_id IS NOT NULL
  AND c_main.id = comp_data.id
        """)
    )



    logger.info(f"Comparison name values filled")

