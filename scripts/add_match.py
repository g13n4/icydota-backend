from collections.abc import Iterable

import click

from constants.task_reason import TaskReason
from tasks.league.process_league import process_game_helper


@click.command()
@click.option('--match_id', '-m', multiple=True, help='Match id to add')
def add_match(match_id: Iterable[int]):
    for mid in match_id:
        process_game_helper(match_id=mid, execute=True, reason=TaskReason.PROCESS_ONE_MATCH_SCRIPT)
        print(f"Added match {mid}")


if __name__ == "__main__":
    add_match()
