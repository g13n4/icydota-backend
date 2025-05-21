from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Game


async def get_games(db_session: AsyncSession, league_id: int):
    match_objs = await (db_session.exec(
        select(Game)
        .where(Game.league_id == league_id)
        .order_by(Game.id)
    ))

    return {
        "games": [
            {
                'value': str(match.id),
                'label': match.name or str(match.id),
            } for match in match_objs.all()]
    }
