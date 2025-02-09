import json

import requests
from sqlmodel import Session

from models import Hero


def create_heroes(db_session: Session) -> list[Hero]:
    r = requests.get('https://api.opendota.com/api/heroes')
    heroes = r.json()
    heroes_dict = dict()
    for hero in heroes:
        hero_id = hero['id']
        new_hero = Hero(
            id=hero_id,
            name=hero['localized_name'],
            npc_name=hero['name']
        )
        heroes_dict[hero_id] = new_hero
    del heroes

    with open('./../../dotaconstants/build/heroes.json') as const_file:
        json_data = json.load(const_file)
        for key, hero_data in json_data.items():
            hero_id = hero_data.get('id', None)
            if hero_id is None:
                raise Exception('No data in constant file')

            hero_obj = heroes_dict[hero_id]
            hero_obj.img_url = hero_data['img']
            hero_obj.icon_url = hero_data['icon']
            db_session.add(hero_obj)

    print("Adding heroes...")
    return [hero for hero in heroes_dict.values()]
