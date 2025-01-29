from typing import ClassVar
from typing import Dict

import sqlalchemy as db
from pydantic import condecimal
from sqlmodel import Field, SQLModel
from sqlmodel import ForeignKey
from constants.performance.window import Ga

column_type = {
    "bigint": db.BIGINT,
    "smallint": db.SMALLINT,
    "basic": db.Integer,
}


def _fk(
        column: str,
        key_name: str = "id",
        col_type: str = "basic",
        cascade: bool = False,
        **column_kwargs,
) -> Field:
    return Field(
        sa_column=db.Column(
            column_type[col_type],
            ForeignKey(
                f"{column}.{key_name}",
                ondelete="CASCADE" if cascade else "SET NULL",
            ),
            nullable=True,
            primary_key=False,
            **column_kwargs,
        ),
    )


DEFAULT_SA_KWARGS = {"cascade": "all,delete", "join_depth": 3, "lazy": "selectin"}


def sa_kwargs_setter(
        add_default: bool = False, *args, **kwargs
) -> Dict[str, str | int]:
    if add_default:
        kwargs = {
            **DEFAULT_SA_KWARGS,
            **kwargs,
        }

    sa_kwargs = dict()
    for arg in args:
        if arg not in DEFAULT_SA_KWARGS:
            raise KeyError
        else:
            sa_kwargs[arg] = DEFAULT_SA_KWARGS[arg]

    for k, v in kwargs.items():
        sa_kwargs[k] = v

    return sa_kwargs


SMALLINT_FIELD_NULLABLE = Field(
    sa_column=db.Column(
        db.SMALLINT,
        nullable=False,
        primary_key=False,
    )
)

SMALLINT_FIELD_NOT_NULLABLE = Field(
    sa_column=db.Column(
        db.SMALLINT,
        nullable=False,
        primary_key=False,
    )
)

