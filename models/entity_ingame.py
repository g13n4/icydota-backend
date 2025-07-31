from typing import Optional

from sqlmodel import Field, SQLModel
import sqlalchemy as db

from models.helpers import _fk
from sqlmodel import Field, Relationship


class Hero(SQLModel, table=True):
    __tablename__ = "heroes"

    id: int = Field(sa_column=db.Column(db.SMALLINT, primary_key=True))  # open_dota id
    name: str = Field(unique=True)

    cdota_name: Optional[str]

    npc_name: Optional[str]
    npc_name_alias: Optional[str]

    # url start https://cdn.cloudflare.steamstatic.com/
    img_url: Optional[str]
    icon_url: Optional[str]

    facets: list["Facet"] = Relationship(
        back_populates="hero",
    )

class Facet(SQLModel, table=True):
    """
    We can get them from dotaconstants provided by opendota.
    Facet in constants == hero_variant (provided by opendota game api) - 1.
    """
    __tablename__ = "facets"

    id: int = Field(sa_column=db.Column(db.SMALLINT, primary_key=True))
    const_id: int

    hero_id: Optional[int] = _fk("heroes", col_type="smallint")
    hero: Optional[Hero] = Relationship(back_populates="facets")

    cdota_name: str
    icon: str
    gradient_id: int
    name: str
    description: str
