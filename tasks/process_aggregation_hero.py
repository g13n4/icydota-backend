from ..celery_app import celery_app
from ..models import League


@celery_app.task(name='aggregate by hero')
def create_aggregation_hero(db_session, league_obj: League):
    pass
#    pgd_ = (db_session.execute(select(League).where(League.league_id == league_obj.id)).first())
