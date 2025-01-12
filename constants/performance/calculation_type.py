from collections import namedtuple
from typing import ClassVar, Any
from enum import Enum

from pydantic import condecimal, BaseModel
from sqlmodel import Field

from constants.helpers import Item


class CalculationFunction(BaseModel):
    gold: Item = Item(value=0)
    xp: Item = Item(value=0)
    lh: Item = Item(value=0)
    movement: Item = Item(value=0)
    level: Item = Item(value=0)
    kills: Item = Item(value=0)
    deaths: Item = Item(value=0)
    kda: Item = Item(value=0)
    obs_placed: Item = Item(value=0)
    sen_placed: Item = Item(value=0)
    stacked: Item = Item(value=0)
    rune_pickups: Item = Item(value=0)
    team_fight_participation: Item = Item(value=0)
    towers_killed: Item = Item(value=0)
    roshans_killed: Item = Item(value=0)
    networth: Item = Item(value=0)


class WindowCalculation(BaseModel):
    category: Item
    name: str
    description: str
