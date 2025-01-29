from sqlmodel import Session

from models import Position


def create_positions(db_session: Session, ) -> None:
    for item in Position.const.POSITIONS:
        position = Position(
            name=item.name,
            id=item.value,
        )
        db_session.add(position)

    print("Create positions...")
