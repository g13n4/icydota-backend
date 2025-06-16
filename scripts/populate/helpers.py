from collections.abc import Hashable
from typing import TypeVar

from sqlmodel import Session, select


T = TypeVar('T')


def get_id_dict(db_session: Session, model: T, field: str | None = None) -> dict[Hashable, T]:
    model_objs = db_session.exec(select(model))
    return { getattr(model, field or 'id'): model for model in model_objs }
