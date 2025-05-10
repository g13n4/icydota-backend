from sqlmodel import Session

from models import Position
from sqlmodel import Session, select


def create_positions(db_session: Session, ) -> None:
    position_objs = db_session.exec(select(Position))
    facet_dict = { x.id: x for x in position_objs }
    if facet_dict:
        print("Positions already created")
        return

    for item in Position.const.POSITIONS:
        position = Position(
            name=item.name,
            id=item.value,
        )
        db_session.add(position)

    print("Create positions...")
