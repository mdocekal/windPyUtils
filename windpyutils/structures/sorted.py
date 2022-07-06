# -*- coding: UTF-8 -*-
""""
Created on 04.07.22
Implementation of sorted data structures.

:author:     Martin Dočekal
"""
import bisect
from abc import abstractmethod
from typing import MutableSet, Iterator, Generic, TypeVar, Iterable, Any, Optional, Tuple, Protocol


class Comparable(Protocol):
    @abstractmethod
    def __lt__(self, other: Any) -> bool: ...


T = TypeVar("T", bound=Comparable)


class SortedSet(MutableSet, Generic[T]):
    """
    Behaves like ordinary set but the value in it are sorted.
    Also, it is more memory efficient as it uses the list to store values.
    """

    def __init__(self, init_values: Optional[Iterable[T]] = None):
        """
        initialization of sorted set

        :param init_values: this values will be used for initialization
        """
        self._values = [] if init_values is None else sorted(init_values)

    def add(self, value: T) -> None:
        insert_index, already_in = self.insertions_index(value)
        if not already_in:
            self._values.insert(insert_index, value)

    def discard(self, value: T) -> None:
        insert_index, already_in = self.insertions_index(value)
        if already_in:
            del self._values[insert_index]

    def __contains__(self, x: T) -> bool:
        # search the smallest interval ends that is greater or equal to x
        try:
            return self.insertions_index(x)[1]
        except TypeError:
            # invalid type so definitely not in
            return False

    def insertions_index(self, x: T) -> Tuple[int, bool]:
        """
        Returns insertions index for given value that remains the value sorted and flag that signalizes whether the
        value is already in.

        :param x: value for which the insertion point should be found
        :return: insertion index and already in flag
        """
        searched_i = bisect.bisect_left(self._values, x)
        try:
            on_index = self._values[searched_i]
            if on_index == x:
                return searched_i, True
        except IndexError:
            pass

        return searched_i, False

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> Iterator[T]:
        yield from iter(self._values)
