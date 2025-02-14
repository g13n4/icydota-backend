import requests
from sqlmodel import Session

from models import Facet, Hero


def create_facets(db_session: Session, heroes: list[Hero]) -> None:
    heroes_dict: dict[str, Hero] = {x.npc_name: x for x in heroes}

    r = requests.get('https://api.opendota.com/api/constants/patch')
    patches = r.json()

    for key, hero_data in patches.items():
        hero_obj: Hero | None = heroes_dict.get(key, None)
        if hero_obj is None:
            raise Exception(f'No object for hero {key}')

        for facet_data in hero_data['facets']:
            facet_idx = facet_data['id']
            new_facet = Facet(
                id=hero_obj.id * 100 + (facet_idx + 1),
                const_id= facet_idx,

                hero_id=hero_obj.id,
                cdota_name=facet_data['name'],
                icon=facet_data['icon'],
                gradient_id=facet_data['gradient_id'],
                name=facet_data['title'],
                description=facet_data['description'],
            )
            db_session.add(new_facet)

    print("Adding facets...")
