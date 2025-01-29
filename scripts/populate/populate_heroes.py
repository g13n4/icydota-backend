import requests
from sqlmodel import Session

from models import Hero


def create_heroes(db_session: Session) -> None:
    r = requests.get('https://api.opendota.com/api/heroes')
    heroes = r.json()
    for hero in heroes:
        new_hero = Hero(
            id=hero['id'],
            name=hero['localized_name'],
            npc_name=hero['name']
        )
        db_session.add(new_hero)

    print("Adding heroes...")
