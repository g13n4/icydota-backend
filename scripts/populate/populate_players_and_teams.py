import requests
from sqlmodel import Session

from models import Player, Team
from scripts.populate.helpers import get_id_dict


def create_players_and_teams(db_session: Session, ) -> None:
    print('Adding players and teams...')
    player_dict = get_id_dict(db_session, Player, 'account_id')
    if player_dict:
        print(f'Players and Teams are already created')
        return

    r = requests.get('https://api.opendota.com/api/proPlayers')
    if r.status_code != 200:
        raise requests.ConnectionError

    players = r.json()

    teams_ids = set()

    players_counter = 0
    teams_counter = 0
    for player in players:
        new_player = Player(
            nickname=player['name'],
            official_name=True,
            account_id=int(player['account_id']),
            steam_id=player['steamid'] and int(player['steamid']), )

        db_session.add(new_player)
        players_counter += 1

        team_id = player['team_id']
        if team_id not in teams_ids:
            new_team = Team(
                id=team_id,
                name=player['team_name'],
                tag=player['team_tag'], )

            db_session.add(new_team)
            teams_ids.add(team_id)
            teams_counter += 1

    print(f'Added {players_counter} players and {teams_counter} teams')
