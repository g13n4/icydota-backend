import os
from typing import Dict

import celery
import requests
from celery import group
from dotenv import load_dotenv
from sqlmodel import Session, select

from constants.task_reason import TaskReason
from db import get_sync_db_session
from models import Game, League
from tasks import set_comparison_names
from tasks.approximate_positions import approximate_positions
from tasks.cron.create_lop_short_data import create_short_data_for_league_cron
from tasks.cron.process_bad_games import attempt_to_process_bad_games_cron
from tasks.cron.process_mispositioned_games import reprocess_mispositioned_league_games_cron
from tasks.league.create_league import get_or_create_league
from tasks.league.process_match import process_game_helper


load_dotenv()

MATCH_ONE_TASK = os.getenv('MATCH_ONE_TASK', default='true')


def get_league_games_tasks(
        league_obj: League | None = None,
        league_id: int | None = None,
        overwrite: bool = False,
        reason: int | None = None,
) -> list:
    db_session: Session = get_sync_db_session(expire=False)

    league_obj = get_or_create_league(db_session=db_session, league_id=league_id, existing_obj=league_obj)

    r = requests.get(f'https://api.opendota.com/api/leagues/{league_id}/matches')
    league_match_data = r.json()

    db_league_games: Dict[int, Game] = { }
    if league_obj:
        db_league_games = { x.id: x for x in league_obj.games }
    new_games_found_list = []

    for idx, game in enumerate(league_match_data):
        if game['match_id'] in db_league_games and not overwrite:
            continue
        else:
            new_games_found_list.append(
                process_game_helper(
                    match_id=game['match_id'],
                    league_id=league_id,
                    execute=False,
                    reason=reason,
                )
            )

    db_session.commit()
    return new_games_found_list


def process_league_task_group(
        league_obj: League | None = None,
        league_id: int | None = None,
        overwrite: bool = False,
        execute: bool = True,
        reason: int | None = TaskReason.PROCESS_LEAGUE,
) -> tuple[int, None | celery.group]:
    tasks = get_league_games_tasks(league_obj=league_obj, league_id=league_id, overwrite=overwrite, reason=reason)

    if tasks:
        task = (
                group(*tasks) |
                approximate_positions.si(league_id=league_id or league_obj.id) |
                set_comparison_names.si(league_id=league_id)
        ).on_error(
            approximate_positions.si(league_id=league_id) | set_comparison_names.si(league_id=league_id)
        )
        if execute:
            task.apply_async()
            return len(tasks), None

        return len(tasks), task

    else:
        return 0, None


def check_leagues_for_correctness():
    db_session: Session = get_sync_db_session(expire=False)
    sel_result = db_session.exec(select(League))

    for league_obj in sel_result.all():
        tasks = get_league_games_tasks(
            league_obj=league_obj,
            league_id=league_obj.id,
            overwrite=False,
            reason=TaskReason.PROCESS_LEAGUE,
        )

        print(f"{len(tasks)} new games found for {league_obj.name}")

        task = (
                reprocess_mispositioned_league_games_cron.si(league_id=league_obj.id)
                | attempt_to_process_bad_games_cron.si(league_id=league_obj.id)
                | group(*tasks)
                | approximate_positions.si(league_id=league_obj.id)
                | create_short_data_for_league_cron.si(league_id=league_obj.id)
                | set_comparison_names.si(league_id=league_obj.id)
        ).on_error(
            approximate_positions.si(league_id=league_obj.id)
            | set_comparison_names.si(league_id=league_obj.id)
        )
        task.apply_async()
