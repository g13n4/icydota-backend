from datetime import datetime

import requests
from sqlmodel import Session

from models.game import Patch


def create_patches(db_session: Session) -> None:
    r = requests.get('https://api.opendota.com/api/constants/patch')
    patch_list = r.json()

    for patch_data in patch_list:
        date = datetime.fromisoformat(patch_data['date'])
        new_facet = Patch(
            id=patch_data['id'],
            name=patch_data['name'],
            date=date.replace(tzinfo=None),
        )
        db_session.add(new_facet)

    print("Adding patches...")
