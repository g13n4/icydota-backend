import requests
from sqlmodel import Session
from sqlmodel import select

from models import Hero


def create_heroes(db_session: Session, update_heroes: bool = False) -> None:
    sel_result = db_session.exec(select(Hero))
    db_heroes = sel_result.all()
    if db_heroes and not update_heroes:
        return

    heroes_db_dict = {x.id: x for x in db_heroes}
    r = requests.get('https://api.opendota.com/api/heroes')
    heroes = r.json()
    for hero in heroes:
        if hero['id'] in heroes_db_dict:
            pass

        new_hero = Hero(
            id=hero['id'],
            name=hero['localized_name'],
            npc_name=hero['name']
        )
        db_session.add(new_hero)

    db_session.commit()


def delete_heroes(db_session: Session) -> None:
    statement = select(Hero)
    hero_objs = db_session.exec(statement).all()
    for hero_obj in hero_objs:
        db_session.delete(hero_obj)
    db_session.commit()
