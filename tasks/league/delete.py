from celery import shared_task
from sqlmodel import Session, delete

from db import get_sync_db_session
from models import League


@shared_task(name="delete_league", ignore_result=True)
def delete_league_task(league_id: int):
    db_session: Session = get_sync_db_session(expire=False)

    db_session.exec(
        delete(League).where(League.id == league_id)
    )
    db_session.commit()
