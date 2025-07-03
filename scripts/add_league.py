import click

from db import get_sync_db_session
from tasks.league.create_league import get_or_create_league


@click.command()
@click.option('--league_id', '-l', help='League id to add')
def add_league(league_id: int):
    db_session = get_sync_db_session(expire=False)
    obj = get_or_create_league(league_id=league_id, db_session=db_session)
    print(f"Added league {league_id} - {obj.name}")


if __name__ == "__main__":
    add_league()
