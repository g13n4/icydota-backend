from sqlmodel import select

from app.models import WindowPositionComparisonType, WindowStatsType, InGamePosition
from ...replay_parsing.ingame_data import POSITION_NAMES
from ...replay_parsing.windows import ALL_WINDOWS


async def create_positions(db_session, ) -> None:
    sel_result = await db_session.execute(select(InGamePosition))
    db_positions = sel_result.scalars().all()
    if db_positions:
        return

    for number, name in POSITION_NAMES.items():
        position = InGamePosition(
            name=name,
            number=number,
        )
        await db_session.add(position)

    await db_session.commit()

    sel_result = await db_session.execute(select(InGamePosition))
    db_positions = sel_result.scalars().all()
    db_positions_dict = {x.number: x for x in db_positions}

    for comparandum, comparans in [[1, 1], [1, 3],
                                   [3, 1], [3, 3],
                                   [2, 2],
                                   [4, 5], [4, 4],
                                   [5, 4], [5, 5],
                                   ]:
        comparandum_obj = db_positions_dict[comparandum]
        comparans_obj = db_positions_dict[comparans]
        position = WindowPositionComparisonType(
            comparandum_id=comparandum_obj.id,
            comparans_id=comparans_obj.id,
            name=f'{comparandum_obj.name} to {comparans_obj.name}',
        )
        await db_session.add(position)

    await db_session.commit()

    # TYPES
    sel_result = await db_session.execute(select(WindowStatsType))
    db_win_info = sel_result.scalars().all()
    if db_win_info:
        return

    for wtype in ALL_WINDOWS.keys():
        wtype_obj = WindowStatsType(
            name=wtype
        )
        db_session.add(wtype_obj)
    await db_session.commit()
