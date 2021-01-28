# -*- coding: UTF-8 -*-
""""
Created on 26.01.21
Module containing map structures.

:author:     Martin Dočekal
"""
import bisect
from typing import Dict, Tuple, Any, Generator

from windpyutils.structures.span_set import SpanSetOverlapsEqRelation, SpanSet


class ImmutIntervalMap:
    """
    Immutable mapping of disjunctive intervals to values.

    Beware that getting value from ends of an interval could be problematic due to float numbers.

    Usage:
        iMap = IntervalMap({(1,100): "first interval", (200,201.5): "second interval"})
        iMap[5]
        "first interval"
    """

    def __init__(self, mapping: Dict[Tuple[float, float], Any]):
        """
        Initialization of a mapping.

        :param mapping: Dictionary that defines the interval mapping.
        Keys must be disjunctive intervals that are defined with a start and end of interval (both inclusive).
        :type mapping: Dict[Tuple[float, float], Any]
        :raise KeyError: When key intervals are not disjunctive or are invalid.
        """

        self._interval_starts = []
        interval_ends = []
        self._values = []
        for (start, end), value in mapping.items():
            if start > end:
                raise KeyError(f"The interval [{start}, {end}] is invalid.")

            self._interval_starts.append(start)
            interval_ends.append(end)
            self._values.append(value)

        # check that intervals are disjunctive
        span_set = SpanSet(self._interval_starts, interval_ends, eq_relation=SpanSetOverlapsEqRelation())

        if len(span_set) != len(mapping):
            raise KeyError("The key intervals are not disjunctive.")

        # this structure is main part used in searching
        self._sortedEnds = []
        self._sortedEndsIndices = []
        for i, e in sorted(enumerate(interval_ends), key=lambda x: x[1]):
            self._sortedEndsIndices.append(i)
            self._sortedEnds.append(e)

    def __len__(self):
        return len(self._interval_starts)

    def __getitem__(self, key: float) -> Any:
        """
        Searches in which interval a given key is.

        :param key: A value from an stored interval.
        :type key: float
        :return: Value associated to the interval in which the given key is.
        :rtype: Any
        """
        # search smallest interval ends that is grater or equal to key
        searched_i = bisect.bisect_left(self._sortedEnds, key)

        if searched_i == len(self._sortedEnds):
            raise KeyError("Provided key is not in any interval.")

        interval_index = self._sortedEndsIndices[searched_i]
        interval_start = self._interval_starts[interval_index]

        if key < interval_start:
            raise KeyError("Provided key is not in any interval.")

        return self._values[interval_index]

    def __iter__(self) -> Generator[Tuple[Tuple[float, float], Any], None, None]:
        """
        Iterates over key intervals and their values. The keys are iterated in ascending order.

        :return: The generator retuns:
                ((interval start, interval end), associated value with interval)
        :rtype: Generator[Tuple[Tuple[float, float], Any], None, None]
        """

        for i, e in zip(self._sortedEndsIndices, self._sortedEnds):
            yield (self._interval_starts[i], e), self._values[i]

    def __contains__(self, key: float):
        try:
            _ = self[key]
            return True
        except KeyError:
            return False
