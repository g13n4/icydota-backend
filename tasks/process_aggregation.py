from ..celery_app import celery_app
from ..models import League


@celery_app.task
def process_aggregation(db_session, league_obj: League):
    pass
    # gad: GameAggregatedData | None = (db_session.execute(select(GameAggregatedData)
    #                                                      .where(GameAggregatedData.league_id == league_obj.id)).first())
    #
    # pgd_objs = (db_session.execute(select(PlayerGameData)
    #                                .where(PlayerGameData.league_id == league_obj.id)).first())
    #
    # if gad:
    #     for gabp in gad.player_agg:
    #
    #
    #
    # else:
