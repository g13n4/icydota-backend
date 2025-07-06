from sqlmodel import Session

from db import get_sync_db_session
from scripts.populate import create_buildings, create_heroes, create_performance_data, \
    create_players_and_teams, create_positions, create_facets, create_patches


def populate_all(db_session: Session | None = None):
    if db_session is None:
        db_session = get_sync_db_session(expire=False)

    print("Adding...")
    create_patches(db_session)
    create_buildings(db_session)
    heroes = create_heroes(db_session)
    create_facets(db_session, heroes)
    create_performance_data(db_session)
    create_players_and_teams(db_session)
    create_positions(db_session)

    db_session.full_commit()

    print("Done!")


if __name__ == "__main__":
    populate_all()
