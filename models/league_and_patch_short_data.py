from typing import Optional, ClassVar

from sqlmodel import Field, SQLModel

from constants.league_and_patch_short_data import LeaguePatchShortDataConstant
from models.mixins.helpers import inherit_annotations
from models.mixins.league_and_patch_short_data import LeagueAndPatchShortDataMixin


@inherit_annotations
class LoPShortDataData(LeagueAndPatchShortDataMixin, SQLModel, table=True):
    __tablename__ = "lop_short_datas"

    const: ClassVar[LeaguePatchShortDataConstant] = LeaguePatchShortDataConstant

    id: Optional[int] = Field(default=None, primary_key=True)

    league_id: Optional[int] = Field(default=None, foreign_key="leagues.id", index=True)
    patch_id: Optional[int] = Field(default=None, foreign_key="patches.id", index=True)
