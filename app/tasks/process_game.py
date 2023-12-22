from ..celery import celery_app
from typing import Dict, List

from sqlmodel import select

from ..celery import celery_app
from ..models import Player, Team, League


def process_teams(db_session, dire_data: dict, radiant_data: dict) -> Dict[str, Team]:
    teams = {
        'radiant': radiant_data,
        'dire': dire_data,
    }

    obj_teams = {
        'radiant': None,
        'dire': None,
    }

    for key, data in teams.items():
        team_obj = db_session.execute(select(Team).where(Team.odota_id == data['team_id']))
        if not team_obj:
            team_obj = Team(
                odota_id=data['team_id'],
                name=data['name'],
                tag=data['tag'],
            )
            db_session.add(team_obj)

        obj_teams[key] = team_obj

    db_session.commit()
    return obj_teams


def process_players(db_session, players: List[dict]) -> Dict[int, Player]:
    players_dict: dict = {x: None for x in range(10)}

    for player in players:
        player_obj = db_session.execute(select(Player).where(Player.steam_id == player['account_id']))
        if not player_obj:
            player_obj = Player(
                nickname=player['name'],
                steam_id=player['account_id']
            )
            db_session.add(player_obj)

        players_dict[players_dict['player_slot']] = player_obj

    return players_dict


@celery_app.task
def process_game(db_session, web_client, match_id: int, league_obj: League):
    r = web_client.get(f'https://api.opendota.com/api/matches/{match_id}')
    game_data = r.json()

    teams_dict = process_teams(db_session, game_data['dire_team'], game_data['radiant_team'])
    players_dict = process_players(db_session, game_data['players'])
