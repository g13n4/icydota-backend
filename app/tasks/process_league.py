from typing import Dict

from .process_game import process_game
from ..celery import celery_app
from ..models import League, Game


@celery_app.task
def process_league(db_session, web_client, league_obj: League):
    r = await web_client.get(f'https://api.opendota.com/api/leagues/{league_obj.league_id}/matches')
    league_match_data = r.json()

    db_league_games: Dict[int, Game] = {x.match_id: x for x in league_obj.games}
    for game in league_match_data:
        if game['match_id'] in db_league_games:
            continue
        else:
            process_game(db_session=db_session,
                         web_client=web_client,
                         match_id=game['match_id'],
                         league_obj=league_obj)
