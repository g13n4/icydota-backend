from datetime import datetime

import requests
from sqlmodel import Session

from models.game import Patch


def create_patches(db_session: Session) -> None:
    r = requests.get('https://api.opendota.com/api/constants/hero_abilities')
    facets = r.json()

    for key, hpatch_data in facets.items():
        new_facet = Patch(
            id=hpatch_data['id'],
            name=hpatch_data['name'],
            date=datetime.fromtimestamp(hpatch_data['date']),
        )
        db_session.add(new_facet)

    print("Adding patches...")
