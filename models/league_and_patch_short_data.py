from datetime import datetime
from typing import Optional, ClassVar

from sqlalchemy import text
from sqlmodel import Field, Relationship, SQLModel

from constants.league_and_patch_short_data import LeaguePatchShortDataConstant
from models.mixins.helpers import inherit_annotations
from models.mixins.league_and_patch_short_data import LeagueAndPatchShortDataMixin, LeagueAndPatchShortDataMomentumMixin


@inherit_annotations
class LoPShortData(LeagueAndPatchShortDataMixin, SQLModel, table=True):
    __tablename__ = "lop_short_data"

    const: ClassVar[LeaguePatchShortDataConstant] = LeaguePatchShortDataConstant

    id: Optional[int] = Field(default=None, primary_key=True)

    league_id: Optional[int] = Field(default=None, foreign_key="leagues.id", index=True)
    patch_id: Optional[int] = Field(default=None, foreign_key="patches.id", index=True)

    momentum: Optional["LoPShortDataMomentum"] = Relationship(back_populates="data")

    partial_comparison: bool = Field(default=False)

    created_at: Optional[datetime] = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )


@inherit_annotations
class LoPShortDataMomentum(LeagueAndPatchShortDataMomentumMixin, SQLModel, table=True):
    __tablename__ = "lop_short_data_momentum"

    const: ClassVar[LeaguePatchShortDataConstant] = LeaguePatchShortDataConstant

    id: Optional[int] = Field(default=None, primary_key=True)

    data_id: Optional[int] = Field(default=None, foreign_key="lop_short_data.id", index=True)
    data: Optional[LoPShortData] = Relationship(back_populates="momentum")

    compared_to: str
