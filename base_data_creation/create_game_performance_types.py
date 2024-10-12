from sqlmodel import Session

from models import GamePerformanceType


def create_game_performance_types(
    db_session: Session,
) -> None:
    for type_id, type_name in GamePerformanceType.TYPES:
        new_type = GamePerformanceType(
            id=type_id,
            name=type_name,
        )

        db_session.add(new_type)

    db_session.commit()
    print("Added types for game performance")
