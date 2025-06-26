from sqlmodel import Session, select

from models import Position


def _format_name(name: str) -> str:
    return " ".join(list(map(lambda x: x.capitalize(), "name".split("_"))))


def create_positions(db_session: Session, ) -> None:
    position_objs = db_session.exec(select(Position))
    facet_dict = { x.id: x for x in position_objs }
    if facet_dict:
        print("Positions already created")
        return

    for item in Position.const.POSITIONS:
        position = Position(
            name=_format_name(item.name),
            id=item.value,
        )
        db_session.add(position)

    print("Create positions...")
