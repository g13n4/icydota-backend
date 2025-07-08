from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Game

def _format_name(name: str | None, game_id: int) -> str:
    if name:
        return f"{name} ({game_id})"
    else:
        return str(game_id)


async def get_games(db_session: AsyncSession, league_id: int):
    match_objs = await (db_session.exec(
        select(Game)
        .where(Game.league_id == league_id, Game.is_broken != True)
        .order_by(Game.id)
    ))

    return {
        "games": [
            {
                'value': str(match.id),
                'label': _format_name(match.name, match.id),
            } for match in match_objs.all()]
    }
