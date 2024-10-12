from typing import Optional

from sqlmodel import Field, SQLModel


class Hero(SQLModel, table=True):
    __tablename__ = "heroes"

    id: int = Field(default=None, primary_key=True)  # open_dota id
    name: str = Field(unique=True, index=True)

    cdota_name: Optional[str]

    npc_name: Optional[str]
    npc_name_alias: Optional[str]


class Facet(SQLModel, table=True):
    __tablename__ = "facets"
    id: int = Field(default=None, primary_key=True)  # open_dota id

    hero_id: Optional[int] = Field(default=None, foreign_key="heroes.id", index=True)
    cdota_name: str = Field(unique=True, index=True)
    icon: str
    gradient_id: int
    name: str
    description: str
