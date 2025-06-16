import requests
from sqlmodel import Session

from models import Hero
from scripts.populate.helpers import get_id_dict


def create_heroes(db_session: Session) -> list[Hero]:
    heroes_dict = get_id_dict(db_session, Hero)

    r = requests.get('https://api.opendota.com/api/heroes')
    heroes = r.json()

    r = requests.get('https://api.opendota.com/api/constants/heroes')
    heroes_additional_data = r.json()

    heroes_add_data_dict = { hero_data['id']: hero_data for _, hero_data in heroes_additional_data.items() }
    heroes_list = []

    for hero in heroes:
        hero_id = hero['id']
        if hero_id is None:
            raise Exception('No data in constant file')

        if (hero_obj := heroes_dict.get(hero_id, None)):
            hero_obj.name = hero['localized_name']
            hero_obj.npc_name = hero['name']
        else:
            hero_obj = Hero(
                id=hero_id,
                name=hero['localized_name'],
                npc_name=hero['name']
            )

        # url start https://cdn.cloudflare.steamstatic.com/
        hero_data = heroes_add_data_dict[hero_id]
        hero_obj.img_url = hero_data['img']
        hero_obj.icon_url = hero_data['icon']

        db_session.add(hero_obj)
        heroes_list.append(hero_obj)

    print("Adding heroes...")
    return heroes_list
