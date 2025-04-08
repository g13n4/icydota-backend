from sqlmodel import Session

from models import Building


def create_buildings(db_session: Session) -> None:
    for lane in Building.const.LANES:
        if lane.value == 0:
            db_session.add(
                Building(
                    name='First tier 4 tower',
                    lane=Building.const.BASE.value,
                    is_tower=True,
                    tier=Building.const.TIER_FOUR.value,
                    first_tower_4=False,
                )
            )
            db_session.add(
                Building(
                    name='Second tier 4 tower',
                    lane=0,
                    is_tower=True,
                    tier=4,
                    first_tower_4=True,
                )
            )

        else:
            for tier in Building.const.TIERS:
                building_obj = Building(
                    name=f"{lane.description} {tier.description} tower",
                    lane=lane.value,
                    is_tower=True,
                    tier=tier.value,
                    first_tower_4=None,

                    is_rax=False,
                )
                db_session.add(building_obj)



    for lane in Building.const.REAL_LANES:
        for rax, rax_name in [[False, 'range barracks'], [True, 'melee barracks'], ]:
            building_obj = Building(
                name=f'{lane.description} {rax_name}',
                lane=lane.value,
                is_tower=False,

                tier=None,
                is_rax=True,
                melee=rax,
            )
            db_session.add(building_obj)

    print("Create buildings...")
