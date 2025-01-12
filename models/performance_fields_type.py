from typing import Optional, ClassVar

from sqlmodel import Field, SQLModel


class PerformanceWindowField(SQLModel, table=True):
    __tablename__ = "performance_window_fields"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    is_active: bool = Field(default=True)


# PERFORMANCE TOTAL
class PerformanceTotalField(SQLModel, table=True):
    __tablename__ = "performance_total_fields"

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    is_active: bool = Field(default=True)
