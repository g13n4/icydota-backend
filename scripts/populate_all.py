from db import get_db
from scripts.populate import create_buildings, create_heroes, create_performance_data, \
    create_players_and_teams, create_positions, create_facets, create_patches


def populate_all():
    db_session = get_db()

    print("Adding...")
    create_patches(db_session)
    create_buildings(db_session)
    heroes = create_heroes(db_session)
    create_facets(db_session, heroes)
    create_performance_data(db_session)
    create_players_and_teams(db_session)
    create_positions(db_session)

    db_session.commit()

    print("Done!")
