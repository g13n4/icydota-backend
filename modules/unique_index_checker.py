from collections.abc import Hashable


class UniqueIndexChecker:
    def __init__(self):
        self.data = set()


    def add(self, value: Hashable):
        if value in self.data:
            raise ValueError("Value is not unique!")

        self.data.add(value)
