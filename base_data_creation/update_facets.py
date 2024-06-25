from pathlib import Path
import json
from sqlmodel import Session, select
from models import Hero, Facet

# use hero_abilities_facets_v1.json from https://github.com/odota/dotaconstants to load facets
def update_facets(db_session: Session, path: str | Path) -> None:
    with open(path, 'r') as hero_abilities_file:
        heroes = db_session.exec(select(Hero))

        heroes_dict = dict()
        for obj in heroes.all():
            heroes_dict[obj.npc_name] = obj
            if obj.npc_name_alias:
                heroes_dict[obj.npc_name_alias] = obj

        hero_abilities_data = json.load(hero_abilities_file)
        for hero_name, hero_data in hero_abilities_data.items():
            facets = hero_data['facets']

            for facet in facets:
                associated_hero = heroes_dict[hero_name]
                facet_obj = Facet(
                    hero_id=associated_hero.id,
                    cdota_name=facet['name'],
                    icon=facet['icon'],
                    gradient_id=facet['gradient_id'],
                    name=facet['title'],
                    description=facet['description'],
                )

                db_session.add(facet_obj)

        db_session.commit()
