from collections.abc import Hashable


def to_proper_name(value: str, split: str = '_') -> str:
    return ' '.join(value.split(split)).capitalize()


class UniqueIndexChecker:
    def __init__(self):
        self.data = set()

    def add(self, value: Hashable):
        if value in self.data:
            raise ValueError("Value is not unique!")

        self.data.add(value)

