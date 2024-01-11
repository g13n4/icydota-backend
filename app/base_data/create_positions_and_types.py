from sqlmodel import select

from app.models import PerformanceDataCategory, Position
from ...replay_parsing.ingame_data import POSITION_NAMES
from ...replay_parsing.windows import ALL_WINDOWS


async def create_positions(db_session, ) -> None:
    sel_result = await db_session.execute(select(Position))
    db_positions = sel_result.scalars().all()
    if db_positions:
        return

    for number, name in POSITION_NAMES.items():
        position = Position(
            name=name,
            number=number,
        )
        await db_session.add(position)

    await db_session.commit()

    # TYPES
    sel_result = await db_session.execute(select(PerformanceDataCategory))
    db_win_info = sel_result.scalars().all()
    if db_win_info:
        return

    for wtype in ALL_WINDOWS.keys():
        wtype_obj = PerformanceDataCategory(
            name=wtype
        )

        db_session.add(wtype_obj)
    await db_session.commit()
