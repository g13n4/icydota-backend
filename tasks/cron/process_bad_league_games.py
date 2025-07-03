from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session, select

from db import get_sync_db_session
from models import Game, PositionApproximation, PlayerGameData
from tasks.league.process_league import process_game_helper


logger = get_task_logger(__name__)


@shared_task(name='process_bad_league_games_(cron)')
def reprocess_bad_league_games_cron() -> None:
    db_session: Session = get_sync_db_session()

    select_query = (
        select(Game.id, Game.league_id)
        .join(PlayerGameData, onclause=Game.id == PlayerGameData.game_id)
        .join(PositionApproximation, onclause=Game.league_id == PositionApproximation.league_id)
        .where(
            PlayerGameData.player_id == PositionApproximation.player_id,
            PlayerGameData.position_id != PositionApproximation.position_id,
        ).distinct()
    )

    games_to_process_again = db_session.exec(select_query).all()

    logger.info(f"Found {len(games_to_process_again)} bad games")

    for game_id, league_id in games_to_process_again:
        process_game_helper(match_id=game_id, league_id=league_id, execute=True)
