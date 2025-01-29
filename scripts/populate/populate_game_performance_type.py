from sqlmodel import Session

from models import GamePerformanceType


def create_game_performance_types(
    db_session: Session,
) -> None:
    for gpt in GamePerformanceType.const.VALUES:
        new_type = GamePerformanceType(
            id=gpt.value,
            name=gpt.name,
            description=gpt.description,
        )

        db_session.add(new_type)

    print("Create Game Performance Types")
