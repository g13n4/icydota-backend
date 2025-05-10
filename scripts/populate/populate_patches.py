from datetime import datetime

import requests
from sqlmodel import Session, select

from models.game import Patch


def create_patches(db_session: Session) -> None:
    r = requests.get('https://api.opendota.com/api/constants/patch')
    patch_list = r.json()

    patches_objs = db_session.exec(select(Patch))
    patches_dict = { x.id: x for x in patches_objs }

    for patch_data in patch_list:
        date = datetime.fromisoformat(patch_data['date'])
        id_ = patch_data['id']
        patch_obj = patches_dict.get(id_, None)

        if patch_obj:
            patch_obj.name = patch_data['name']
            patch_obj.date = date.replace(tzinfo=None)

        else:
            patch_obj = Patch(
                id=patch_data['id'],
                name=patch_data['name'],
                date=date.replace(tzinfo=None),
            )
        db_session.add(patch_obj)

    print("Adding patches...")
