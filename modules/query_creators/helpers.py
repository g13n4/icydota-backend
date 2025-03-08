from collections import namedtuple
from typing import Any

from sqlalchemy import Select
from sqlmodel import select
from sqlmodel.sql._expression_select_cls import SelectBase


def create_join_dict(target, onclause, isouter: bool = False):
    return {
        "target": target,
        "onclause": onclause,
        "isouter": isouter,
    }


class JoinList:
    def __init__(self, iterable=None):
        self.data = []
        if iterable is not None:
            for item in iterable:
                self.data.append(item)


    def add(self, target, onclause, isouter: bool = False):
        """Adds a join clause the end of the end JoinList"""
        self.data.append(create_join_dict(target=target, onclause=onclause, isouter=isouter))


    def insert(self, target, onclause, isouter: bool = False, *, index: int = 0):
        """Adds a join clause the end of the beginning of JoinList"""
        self.data.insert(index, create_join_dict(target=target, onclause=onclause, isouter=isouter))


    def __iter__(self):
        return iter(self.data)


    def clear(self):
        self.data = []


ModelItem = namedtuple('ModelItem', ['model', 'name', 'is_header'])


class ModelList:
    def __init__(self, iterable=None):
        self.data: list[ModelItem] = []
        if iterable is not None:
            for item in iterable:
                self.data.append(item)


    def add(self, model, name: str | None = None, is_header: bool = False):
        if name is None:
            name = model.__name__.lower()
        self.data.append(ModelItem(model, name, is_header))


    def __iter__(self):
        return iter(self.data)


    def get_models(self) -> list:
        return [item.model for item in self.data]


    def get_names(self, only_header: bool = False) -> list[str]:
        if only_header:
            return [item.name for item in self.data if item.is_header]
        else:
            return [item.name for item in self.data]


    def clear(self):
        self.data = []


def combine_select(
        models: list,
        joins: list | JoinList,
        where_clauses: ModelList | list,
) -> SelectBase[Any] | Select[tuple[Any]]:
    select_qr = select(*models)
    for join_ in joins:
        select_qr = select_qr.join(**join_)
    select_qr = select_qr.where(*where_clauses)
    return select_qr
