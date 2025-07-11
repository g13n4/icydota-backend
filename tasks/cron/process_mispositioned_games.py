from collections import defaultdict

from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session, select

from constants.task_reason import TaskReason
from db import get_sync_db_session
from models import Game, PositionApproximation, PlayerGameData, Player, League
from tasks.league.process_league import process_game_helper


logger = get_task_logger(__name__)


@shared_task(name='reprocess_mispositioned_league_games_(cron)', ignore_result=True)
def reprocess_mispositioned_league_games_cron() -> None:
    db_session: Session = get_sync_db_session(expire=True)

    player_information_select_query = (
        select(
            League.name,
            Game.league_id,
            Game.name,
            Game.id,
            Player.nickname,
            PositionApproximation.position_id,
            PlayerGameData.position_id,
        )
        .join(PlayerGameData, onclause=Game.id == PlayerGameData.game_id)
        .join(PositionApproximation, onclause=Game.league_id == PositionApproximation.league_id)
        .join(Player, onclause=Player.account_id == PlayerGameData.player_id)
        .join(League, onclause=League.id == Game.league_id)
        .where(
            PlayerGameData.player_id == PositionApproximation.player_id,
            PlayerGameData.position_id != PositionApproximation.position_id,
        )
    )

    player_information_data = db_session.exec(player_information_select_query).all()

    game_to_recalculate = set()
    league_name_dict = dict()
    league_info = defaultdict(list)
    for league_name, league_id, game_name, game_id, nickname, pos_approx, pos_calculated_with in player_information_data:

        game_to_recalculate.add((league_id, game_id))

        league_name_dict[league_id] = league_name

        league_info[league_id].append(
            f"{game_name}: {nickname} was pos {pos_calculated_with} now pos {pos_approx}"
        )
    if len(game_to_recalculate):
        logger.info(f"Found {len(game_to_recalculate)} bad games:")

        for league_id, league_name in league_name_dict.items():
            league_games_found = len(league_info[league_id])
            logger.info(f"Found {league_games_found} for league {league_name}:")

            for message in league_info[league_id]:
                logger.info(message)

        for league_id, game_id in game_to_recalculate:
            process_game_helper(
                match_id=game_id,
                league_id=league_id,
                execute=True,
                reason=TaskReason.PROCESS_MISPOSITIONED_GAMES_CRON,
            )
    else:
        logger.info(f"Found no bad games.")

    db_session.close()
