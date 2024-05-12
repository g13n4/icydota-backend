from sqlmodel import Session
from sqlmodel import select

from models import PerformanceDataCategory

DESCRIPTION_DICT = {
    "interval": {
        "label": "In-game data",
        "description": "Data that is collected by Dota 2 client and is shown to spectators or after the game.",
    },
    "pings": {
        "label": "Pings",
        "description": "Data regarding players pings",
    },
    "damage": {
        "label": "Damage",
        "description": "Data regarding hero damage. Both received and dealt",
    },
    "wards": {
        "label": "Wards",
        "description": "Data regarding wards placed",
    },
    "deward": {
        "label": "Deward",
        "description": "Data regarding dewarding",
    },
    "xp": {
        "label": "XP",
        "description": "Data regarding experience acquisition",
    },
    "gold": {
        "label": "Gold",
        "description": "Data regarding gold acquisition",
    },
}

def update_category_data(db_session: Session) -> None:
    statement = select(PerformanceDataCategory)
    cat_objs = db_session.exec(statement).all()
    for cat_obj in cat_objs:
        if (cat_dict := DESCRIPTION_DICT.get(cat_obj.name, None)):
            cat_obj.label = cat_dict['label']
            cat_obj.description = cat_dict['description']
            db_session.add(cat_obj)
    db_session.commit()

