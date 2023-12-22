from sqlmodel import select

from app.models import InGameBuildingLane, InGameBarracks, InGameBuilding


def _capitalise_first_letter(text: str) -> str:
    return text[0].capitalize() + text[1:]


def _generate_tower_name(lane: InGameBuildingLane, tier: int):
    return f'{_capitalise_first_letter(lane.name)} tier {tier} tower'


async def create_heroes(db_session) -> None:
    sel_result = await db_session.execute(select(InGameBuilding))
    towers = sel_result.scalars().all()
    if towers:
        return
    # 'value': 1, 'name': 'bot',
    for name, lane_num in [[1, 'bot'], [2, 'mid'], [3, 'top'], ]:
        lane_obj = InGameBuildingLane(
            lane=name,
            lane_num=lane_num,
        )
        await db_session.add(lane_obj)

    for melee_bool, name in [[False, 'range barracks'], [True, 'melee barracks'], ]:
        rax = InGameBarracks(
            melee=melee_bool,
            name=name,
        )
        await db_session.add(rax)

    await db_session.commit()

    sel_result = await db_session.execute(select(InGameBuildingLane))
    lanes = sel_result.scalars().all()

    for lane in lanes:
        for tier in range(1, 3):
            building_obj = InGameBuilding(
                name=_generate_tower_name(lane, tier),
                lane=lane.id,
                is_tower=True,
                tier=tier,
            )
            await db_session.add(building_obj)

    await db_session.add(InGameBuilding(
        name='First tier 4 tower',
        is_tower=True,
        tier=4,
        tower4=False,
    ))
    await db_session.add(InGameBuilding(
        name='Second tier 4 tower',
        is_tower=True,
        tier=4,
        tower4=True,
    ))

    sel_result = await db_session.execute(select(InGameBarracks))
    rax_pl = sel_result.scalars().all()

    for lane in lanes:
        for rax in rax_pl:
            building_obj = InGameBuilding(
                name=_capitalise_first_letter(f'{lane.name} {rax.name}'),
                lane=lane.id,
                is_tower=False,
                rax=rax.id,
            )
            await db_session.add(building_obj)

    await db_session.commit()
