from typing import Optional

from sqlmodel import Field, SQLModel
import sqlalchemy as db

from models.helpers import _fk


class Hero(SQLModel, table=True):
    __tablename__ = "heroes"

    id: int = Field(sa_column=db.Column(db.SMALLINT, primary_key=True))  # open_dota id
    name: str = Field(unique=True, index=True)

    cdota_name: Optional[str]

    npc_name: Optional[str]
    npc_name_alias: Optional[str]

    # url start https://cdn.cloudflare.steamstatic.com/
    img_url: Optional[str]
    icon_url: Optional[str]


class Facet(SQLModel, table=True):
    """We can get them from dotaconstants provided by opendota.
    Facet in constants == hero_variant (provided by opendota game api) - 1.
    """
    __tablename__ = "facets"

    id: int = Field(sa_column=db.Column(db.SMALLINT, primary_key=True))
    const_id: int

    hero_id: Optional[int] = _fk("heroes", col_type="smallint")
    cdota_name: str = Field(unique=True, index=True)
    icon: str
    gradient_id: int
    name: str
    description: str
