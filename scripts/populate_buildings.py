from db import get_sync_db_session
from sqlmodel import Session
from sqlmodel import select

from models import Building


def _capitalise_first_letter(text: str) -> str:
    return text[0].capitalize() + text[1:]


def _generate_tower_name(lane: int, tier: int):
    return f'{_capitalise_first_letter(LANE_TO_NAME[lane])} tier {tier} tower'


def create_buildings(db_session: Session) -> None:
    for lane in Building.const.LANES:
        if lane.value == 0:
            continue

        for tier in Building.const.TIERS:
            building_obj = Building(
                name=_generate_tower_name(lane.value, tier.value),
                lane=lane.value,
                is_tower=True,
                tier=tier.value,
                tower4=None,

                is_rax=False,
            )
            db_session.add(building_obj)

    db_session.add(Building(
        name='First tier 4 tower',
        lane=Building.const.BASE.value,
        is_tower=True,
        tier=Building.const.TIER_FOUR.value,
        first_tower_4=False,
    ))
    db_session.add(Building(
        name='Second tier 4 tower',
        lane=0,
        is_tower=True,
        tier=4,
        first_tower_4=True,
    ))

    for lane in [1, 2, 3]:
        for rax, rax_name in [[False, 'range barracks'], [True, 'melee barracks'], ]:
            building_obj = InGameBuilding(
                name=_capitalise_first_letter(f'{LANE_TO_NAME[lane]} {rax_name}'),
                lane=lane,
                is_tower=False,

                tier=None,
                is_rax=True,
                melee=rax,
            )
            db_session.add(building_obj)



def populate_db():
    db_session = get_sync_db_session()
