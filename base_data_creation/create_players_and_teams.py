import requests
from sqlmodel import Session
from sqlmodel import select

from models import Player, Team


def create_players_and_teams(db_session: Session, ) -> None:
    r = requests.get('https://api.opendota.com/api/proPlayers')
    players = r.json()

    teams_ids = set()

    for player in players:
        new_player = Player(
            nickname=player['name'],
            account_id=player['account_id'],
            steam_id=player['steamid'], )

        db_session.add(new_player)

        team_id = player['team_id']
        if team_id not in teams_ids:
            new_team = Team(
                odota_id=team_id,
                name=player['team_name'],
                tag=player['team_tag'], )

            db_session.add(new_team)
            teams_ids.add(team_id)

    db_session.commit()


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
