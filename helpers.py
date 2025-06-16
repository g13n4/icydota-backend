from typing import TypeVar


T = TypeVar('T')


def to_proper_name(value: str, split: str = '_') -> str:
    return ' '.join(value.split(split)).capitalize()
