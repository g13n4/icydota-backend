from sqlmodel import Session
from sqlmodel import select

from models import InGameBuilding

LANE_TO_NAME = {1: 'bot', 2: 'mid', 3: 'top'}


def _capitalise_first_letter(text: str) -> str:
    return text[0].capitalize() + text[1:]


def _generate_tower_name(lane: int, tier: int):
    return f'{_capitalise_first_letter(LANE_TO_NAME[lane])} tier {tier} tower'


def create_buildings(db_session: Session) -> None:
    for lane in [1, 2, 3]:
        for tier in range(1, 4):
            building_obj = InGameBuilding(
                name=_generate_tower_name(lane, tier),
                lane=lane,
                is_tower=True,
                tier=tier,
                tower4=None,

                is_rax=False,
            )
            db_session.add(building_obj)

    db_session.add(InGameBuilding(
        name='First tier 4 tower',
        lane=0,
        is_tower=True,
        tier=4,
        tower4=False,
    ))
    db_session.add(InGameBuilding(
        name='Second tier 4 tower',
        lane=0,
        is_tower=True,
        tier=4,
        tower4=True,
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

    db_session.commit()


def delete_buildings(db_session: Session) -> None:
    statement = select(InGameBuilding)
    IGM_objs = db_session.exec(statement).all()
    for IGM_obj in IGM_objs:
        db_session.delete(IGM_obj)
    db_session.commit()
