# -*- coding: UTF-8 -*-
""""
Created on 23.03.20
Circular buffer implementation.

:author:     Martin Dočekal
"""
from typing import Any, Sequence


class CircularBuffer(Sequence):
    """
    Implementation of circular buffer.
    """

    def __init__(self, max_size: int):
        """
        Implementation of circular butter.

        :param max_size: The max size of circular buffer.
            Must be grater than 0.
        :type max_size: int
        :raise AssertionError: When you provide invalid max size.
        """

        assert max_size > 0

        self._buffer = [None] * max_size
        self._size = 0
        self._offset = 0  # Offset for next element that will be added.

    def __len__(self) -> int:
        """
        Actual size of buffer.

        :return: Actual size of buffer.
        :rtype: int
        """

        return self._size

    def __getitem__(self, offset: int) -> Any:
        """
        Get item on offset.

        Time complexity: O(1)

        :param offset: The offset of item you want.
        :type offset: int
        :return: Element on given offset.
        :rtype: Any
        :raise IndexError: when you touch outside the actual size of buffer.
        """

        if offset >= len(self) or 0 > offset:
            raise IndexError("The offset {} is out of buffer.".format(offset))

        return self._buffer[(self._offset-self._size+offset) % self.max_size]

    @property
    def max_size(self) -> int:
        """
        Maximum buffer size
        """

        return len(self._buffer)

    def put(self, e: Any):
        """
        Put element into circular buffer.

        Time complexity: O(1)

        :param e: Element you want to add.
        :type e: Any
        """

        self._buffer[self._offset] = e
        self._offset = (self._offset + 1) % self.max_size

        if self._size < self.max_size:
            self._size += 1

    def clear(self):
        """
        Removes all items from buffer.

        Time complexity: O(1)
        """

        self._size = 0
        self._offset = 0
