from sqlmodel import select

from ..celery import celery_app
from ..models import League


@celery_app.task
def create_aggregation_hero(db_session, league_obj: League):
    pgd_ = (db_session.execute(select(League).where(League.league_id == league_obj.id)).first())

    GameAggregatedByPlayer
