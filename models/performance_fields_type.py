from typing import Optional

import sqlalchemy as db
from sqlmodel import Field, SQLModel


class PerformanceWindowField(SQLModel, table=True):
    __tablename__ = "performance_window_fields"

    # id from const
    id: Optional[int] = Field(sa_column=db.Column(db.SMALLINT, primary_key=True))

    name: str
    is_active: bool = Field(default=True)


# PERFORMANCE TOTAL
class PerformanceTotalField(SQLModel, table=True):
    __tablename__ = "performance_total_fields"

    # id from const
    id: Optional[int] = Field(sa_column=db.Column(db.SMALLINT, primary_key=True))

    field_id: int
    name: str
    is_active: bool = Field(default=True)


