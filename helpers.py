import re
from typing import TypeVar


CAMEL_CASE_MATCH = re.compile(r'_([a-z])')


def snake_to_camel(snake_str):
    return CAMEL_CASE_MATCH.sub(lambda m: m.group(1).upper(), snake_str)


T = TypeVar('T')


def to_proper_name(value: str, split: str = '_') -> str:
    return ' '.join(value.split(split)).capitalize()
