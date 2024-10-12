from typing import Optional

from sqlmodel import Field, SQLModel


class PositionApproximation(SQLModel, table=True):
    __tablename__ = "approximated_positions"

    id: Optional[int] = Field(default=None, primary_key=True)

    league_id: Optional[int] = Field(default=None, foreign_key="leagues.id")
    player_id: Optional[int] = Field(default=None, foreign_key="players.account_id")
    position_id: Optional[int] = Field(default=None, foreign_key="positions.id")
