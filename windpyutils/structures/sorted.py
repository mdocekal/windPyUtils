# -*- coding: UTF-8 -*-
""""
Created on 04.07.22
Implementation of sorted data structures.

:author:     Martin Dočekal
"""
import bisect
from abc import abstractmethod
from typing import MutableSet, Iterator, Generic, TypeVar, Iterable, Any, Optional, Tuple, Protocol, Mapping, \
    MutableMapping

from windpyutils.generic import arg_sort


class Comparable(Protocol):
    @abstractmethod
    def __lt__(self, other: Any) -> bool: ...


K = TypeVar("K", bound=Comparable)
T = TypeVar("T", bound=Comparable)


class SortedMap(MutableMapping[K, T], Generic[K, T]):
    """
    Behaves like ordinary map but the keys in it are sorted (not according to set history).
    Also, it is more memory efficient as it uses lists to store keys and values. Might be slower than ordinary map.
    """

    def __init__(self, init_values: Optional[Mapping[K, T]] = None):
        """
        :param init_values: voluntary initial values for the map.
        """
        self._keys = []
        self._values = []

        if init_values is not None:
            self._keys = list(init_values.keys())
            # sort keys
            sorted_indices = arg_sort(self._keys)
            values = list(init_values.values())
            self._keys = [self._keys[i] for i in sorted_indices]
            self._values = [values[i] for i in sorted_indices]

    def __getitem__(self, key: K) -> T:
        insert_index, already_in = self.insertions_index(key)
        if not already_in:
            raise KeyError(f"Key {key} is not in the map.")

        return self._values[insert_index]

    def __setitem__(self, key: K, value: T) -> None:
        if not (isinstance(key, float) or isinstance(key, int)) or key != key:
            raise TypeError("Is not a valid key.")

        insert_index, already_in = self.insertions_index(key)
        if already_in:
            self._values[insert_index] = value
        else:
            self._keys.insert(insert_index, key)
            self._values.insert(insert_index, value)

    def __delitem__(self, key: K) -> None:
        insert_index, already_in = self.insertions_index(key)
        if not already_in:
            raise KeyError(f"Key {key} is not in the map.")

        del self._keys[insert_index]
        del self._values[insert_index]

    def __iter__(self) -> Iterator[K]:
        return iter(self._keys)

    def __len__(self) -> int:
        return len(self._keys)

    def insertions_index(self, x: T) -> Tuple[int, bool]:
        """
        Returns insertions index for given value that remains the value sorted and flag that signalizes whether the
        value is already in.

        :param x: value for which the insertion point should be found
        :return: insertion index and already in flag
        """
        searched_i = bisect.bisect_left(self._keys, x)
        try:
            on_index = self._keys[searched_i]
            if on_index == x:
                return searched_i, True
        except IndexError:
            pass

        return searched_i, False


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
        self._values = []

        if init_values is not None:
            sorted_vals = sorted(init_values)
            # check uniqueness
            self._values.append(sorted_vals[0])
            for i in range(1, len(sorted_vals)):
                if sorted_vals[i] != sorted_vals[i - 1]:
                    self._values.append(sorted_vals[i])

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
