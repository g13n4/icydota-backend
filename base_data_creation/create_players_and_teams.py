import requests
from sqlmodel import Session, select

from models import Player, Team


def create_players_and_teams(db_session: Session, ) -> None:
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

    db_session.commit()
    print(f'Added {players_counter} players and {teams_counter} teams')


def delete_all_players_and_teams(db_session: Session, ) -> None:
    statement = select(Player)
    player_objs = db_session.exec(statement).all()
    for player_obj in player_objs:
        db_session.delete(player_obj)

    statement = select(Team)
    teams_objs = db_session.exec(statement).all()
    for team_obj in teams_objs:
        db_session.delete(team_obj)

    db_session.commit()


def set_official_name_to_true(db_session: Session, ):
    statement = select(Player)
    player_objs = db_session.exec(statement).all()
    for player_obj in player_objs:
        player_obj.official_name = True
        db_session.add(player_obj)

    db_session.commit()
