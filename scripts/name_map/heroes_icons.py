from sqlmodel import select

from db import get_sync_db_session
from models import Hero
from scripts.name_map.processing import check_data_map


HEROES_ICONS = "heroes_icons"


def create_heroes_to_icons_map():
    db_session = get_sync_db_session(expire=True)
    query = db_session.exec(select(Hero.name, Hero.icon_url))

    output = dict()
    for name, icon_url in query.all():
        output[name] = icon_url

    db_session.close()
    return output


def check_initial_heroes_icons(func_type: str, **kwargs) -> bool:
    return check_data_map(
        func_type=func_type,
        data_creation=create_heroes_to_icons_map,
        file_name_const=HEROES_ICONS,
        **kwargs
    )
