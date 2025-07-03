from collections.abc import Iterable

import click

from db import get_sync_db_session
from tasks.league.create_league import get_or_create_league


@click.command()
@click.option('--league_id', '-l', multiple=True, help='League id to add')
def add_league(league_id: Iterable[int]):
    for lid in league_id:
        db_session = get_sync_db_session(expire=False)
        get_or_create_league(league_id=lid, db_session=db_session)
        print(f"Added league {lid}")


if __name__ == "__main__":
    add_league()
