import bisect
import sys
from collections.abc import Iterable


class SmallestFitFinder:
    """
    Helps to find the smallest number in a list that a value is bigger than
    Example:
        data = [1, 3, 5, 7, 9]
        find(2) => 1
    """
    def __init__(self, data: Iterable[int]):
        self._data = list(data)
        self._first_value = sys.maxsize

        self._update_state()


    def _update_state(self):
        self._data.sort()
        self._first_value = self._data[0]
        return


    def extend(self, data: Iterable[int]) -> None:
        for value in data:
            self._data.append(value)

        self._update_state()
        return


    def add(self, value: int) -> None:
        self._data.append(value)

        self._update_state()
        return


    def find(self, value: int) -> int:
        if value < self._first_value:
            raise ValueError(f"Impossible to find a fit for value {value} in {self._data}")

        index = bisect.bisect_left(self._data, value)
        if index >= len(self._data):
            return self._data[-1]

        fit = self._data[index]
        # fit can only be bigger or equal to value
        # if the fit is bigger then bisect returned a next value after the one we need
        if fit > value:
            return self._data[index - 1]
        # fit is equal to value which means the index was correct
        else:
            return fit
