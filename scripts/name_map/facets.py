from pathlib import Path

from sqlmodel import select

from db import get_sync_db_session
from models import Facet
from scripts.name_map.processing import check_data_map


FACETS_NAME = "facets"


def create_facets_fields_map():
    db_session = get_sync_db_session(expire=True)
    query = db_session.exec(select(Facet.hero_id, Facet.const_id, Facet.name, Facet.description))

    output = dict()
    for hero_id, facet_id, name, description in query.all():
        if hero_id not in output:
            output[hero_id] = { }

        output[hero_id][facet_id] = {
            "name": name,
            "description": description
        }

    db_session.close()
    return output


def check_initial_facets_map(func_type: str, **kwargs) -> bool:
    return check_data_map(
        func_type=func_type,
        data_creation=create_facets_fields_map,
        file_name_const=FACETS_NAME,
        **kwargs
    )
