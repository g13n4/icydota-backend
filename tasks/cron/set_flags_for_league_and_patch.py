import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session, select

from db import get_sync_db_session
from models import Game, League, Patch


logger = get_task_logger(__name__)


@shared_task(name='set_leagues_and_patch_flags_(cron)', ignore_result=True)
def set_leagues_and_patch_flags_cron(league_id: int) -> None:
    db_session: Session = get_sync_db_session(expire=True)

    now = datetime.datetime.now()

    league_obj = db_session.get(League, league_id)

    league_obj.processed_at = now
    db_session.add(league_obj)

    patch_select = db_session.exec(
        select(Patch)
        .join(Game, onclause=Patch.id == Game.patch_id)
        .join(League, onclause=League.id == Game.league_id)
        .where(League.id == league_id)
    )

    for patch_obj in patch_select.all():
        patch_obj.processed_at = now
        db_session.add(patch_obj)

    db_session.full_commit()
