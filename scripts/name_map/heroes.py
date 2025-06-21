from sqlmodel import select

from db import get_sync_db_session
from models import Hero
from scripts.name_map.processing import check_data_map


HEROES_NAME = "heroes"


def create_heroes_fields_map():
    db_session = get_sync_db_session(expire=True)
    query = db_session.exec(select(Hero.id, Hero.name, Hero.img_url, Hero.icon_url))

    output = dict()
    for hero_id, name, img_url, icon_url in query.all():
        if hero_id not in output:
            output[hero_id] = { }

        output[hero_id] = {
            "name": name,
            "img_url": img_url,
            "icon_url": icon_url,
        }

    db_session.close()
    return output


def check_initial_heroes_map(func_type: str, **kwargs) -> bool:
    return check_data_map(
        func_type=func_type,
        data_creation=create_heroes_fields_map,
        file_name_const=HEROES_NAME,
        **kwargs
    )
