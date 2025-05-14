import bisect
from collections.abc import Iterable


class SmallestFitFinter:
    def __init__(self, data: Iterable[int]):
        self._data = list(data)
        self._data.sort()


    def extend(self, data: Iterable[int]) -> None:
        for value in data:
            self._data.append(value)
        self._data.sort()
        return


    def add(self, value: int) -> None:
        self._data.append(value)
        self._data.sort()
        return


    def find(self, value: int) -> int:
        index = bisect.bisect_left(self._data, value)
        fit = self._data[index]
        if fit != value:
            fit = self._data[index - 1]
        return fit
