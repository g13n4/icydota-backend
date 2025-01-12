from pydantic import BaseModel
from constants.helpers import Item


class WindowCategories(BaseModel):
    interval: Item(value=1)
    pings: Item(value=2)
    damage: Item(value=3)
    wards: Item(value=4)
    deward: Item(value=5)
    xp: Item(value=6, description='XP')
    gold: Item(value=7)
