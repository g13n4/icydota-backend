from sqlmodel import Session
from sqlmodel import select

from models import Position
from replay_parsing.ingame_data import POSITION_NAMES


def create_positions(db_session, ) -> None:
    sel_result = db_session.execute(select(Position))
    db_positions = sel_result.scalars().all()
    if db_positions:
        return

    for number, name in POSITION_NAMES.items():
        position = Position(
            name=name,
            number=number,
        )
        db_session.add(position)

    db_session.commit()


def delete_positions(db_session: Session) -> None:
    statement = select(Position)
    POS_objs = db_session.exec(statement).all()
    for pos_obj in POS_objs:
        db_session.delete(pos_obj)
    db_session.commit()
