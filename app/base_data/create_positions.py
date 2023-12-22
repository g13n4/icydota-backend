from sqlmodel import select

from app.models import InGamePosition, WindowComparisonType
from ...replay_parsing.ingame_data import POSITION_NAMES


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
        position = WindowComparisonType(
            comparandum=comparandum_obj.id,
            comparans=comparans_obj.id,
            name=f'{comparandum_obj.name} to {comparans_obj.name}',
        )
        await db_session.add(position)

    await db_session.commit()
