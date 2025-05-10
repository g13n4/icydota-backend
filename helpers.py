from collections.abc import Hashable
from typing import TypeVar

from sqlmodel import Session, select


T = TypeVar('T')


def to_proper_name(value: str, split: str = '_') -> str:
    return ' '.join(value.split(split)).capitalize()


class UniqueIndexChecker:
    def __init__(self):
        self.data = set()


    def add(self, value: Hashable):
        if value in self.data:
            raise ValueError("Value is not unique!")

        self.data.add(value)


def get_id_dict(db_session: Session, model: T, field: str | None = None) -> dict[Hashable, T]:
    model_objs = db_session.exec(select(model))
    return { getattr(model, field or 'id'): model for model in model_objs }
