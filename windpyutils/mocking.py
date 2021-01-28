# -*- coding: UTF-8 -*-
""""
Created on 13.05.20
This module contains structures that are useful for mocking.

:author:     Martin Dočekal
"""
from abc import ABC, abstractmethod
from itertools import count
from typing import Sequence, Union, Iterator

from windpyutils.generic import RoundSequence


class BasicMockedRand(ABC):
    """
    Basic abstract class for mock rands.
    Every class must have gen parameter returning iterator that on next call return next value.
    """

    def __call__(self, *args, **kwargs):
        return next(self.gen)

    @property
    @abstractmethod
    def gen(self) -> Iterator:
        pass

    def sample(self):
        """
        Same as a simple call.
        """
        return self()


class MockedRand(BasicMockedRand):
    """
    Mock that has deterministic rand like behaviour.

    It can operate in two modes:
        Steps
            Init example: m = MockedRand(0.1)
                0   0.1     0.2 ...
            Every call returns value:
                N*STEP - int(N*STEP)
            Where N is zero, first to n-th call. STEP is parameter provided in the initialization.

        Sequence
            Init example: m = MockedRand([0.1, 0.2, 0.6])
            Every call returns next value from provided collection. When reaches the end it start from beginning again.
    """

    class Counter(object):

        def __init__(self, step):
            self.step = step
            self.cnt = -1

        def __next__(self):
            self.cnt += 1
            tmp = self.step * self.cnt
            return tmp - int(tmp)

    def __init__(self, use: Union[Sequence[float], float] = None):
        """
        Initialization of he mock.

        :param use: Collection that will be used for generating or generator step.
        :type use: Union[Sequence[float], float]
        """

        if isinstance(use, float) or isinstance(use, int):
            self._gen = self.Counter(use)
        else:
            self._gen = RoundSequence(use)

    @property
    def gen(self):
        return self._gen


class MockedRandInt(BasicMockedRand):
    """
    Mock that has deterministic randint like behaviour.

    It can operate in two modes:
        Default
            Init example: m = MockRandInt()
            Every call returns value of a call counter from 0 (first call returns 0) to N*STEP.

        Sequence
            Init example: m = MockRandInt([1, 1, 0, 0, 2, 0, 1])
            Every call returns next value from provided collection. When reaches the end it start from beginning again.
    """

    def __init__(self, use: Union[Sequence[int], int]):
        """
        Initialization of he mock.

        :param use: Collection that will be used for generating or generator step.
        :type use: Union[Sequence[int], int]
        """

        if isinstance(use, float) or isinstance(use, int):
            self._gen = count(0, use)
        else:
            self._gen = RoundSequence(use)

    @property
    def gen(self):
        return self._gen
