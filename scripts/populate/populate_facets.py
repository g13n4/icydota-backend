import requests
from sqlmodel import Session, select

from models import Facet, Hero


def create_facets(db_session: Session, heroes: list[Hero]) -> None:
    heroes_dict: dict[str, Hero] = { x.npc_name: x for x in heroes }
    facet_objs = db_session.exec(select(Facet))
    facet_dict = { x.id: x for x in facet_objs }

    r = requests.get('https://api.opendota.com/api/constants/hero_abilities')
    facets = r.json()

    for key, hero_data in facets.items():
        hero_obj: Hero | None = heroes_dict.get(key, None)
        if hero_obj is None:
            raise Exception(f'No object for hero {key}')

        for facet_data in hero_data['facets']:
            facet_idx = facet_data['id']
            db_facet_id = hero_obj.id * 100 + (facet_idx + 1)

            if (facet_obj := facet_dict.get(db_facet_id, None)):
                facet_obj.cdota_name=facet_data['name']
                facet_obj.icon=facet_data['icon']
                facet_obj.gradient_id=facet_data['gradient_id']
                facet_obj.name=facet_data['title']
                facet_obj.description=facet_data['description']
            else:
                facet_obj = Facet(
                    id=db_facet_id,
                    const_id=facet_idx,

                    hero=hero_obj,
                    cdota_name=facet_data['name'],
                    icon=facet_data['icon'],
                    gradient_id=facet_data['gradient_id'],
                    name=facet_data['title'],
                    description=facet_data['description'],
                )

            db_session.add(facet_obj)

    print("Adding facets...")
