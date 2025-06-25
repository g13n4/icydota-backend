from sqlmodel.ext.asyncio.session import AsyncSession

from models import Game


async def get_match_name_data(adb_session: AsyncSession, match_id: str | int) -> dict[str, str | bool]:
    game_obj = await adb_session.get(Game, match_id)
    sent_name, dire_win = game_obj.name.split(" vs ")

    return {
        "direName": dire_win,
        "sentName": sent_name,
        "hasDireWon": game_obj.dire_win,
    }
