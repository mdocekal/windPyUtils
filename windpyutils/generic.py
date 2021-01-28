# -*- coding: UTF-8 -*-
""""
Created on 31.01.20
This module contains generic utils

:author:     Martin Dočekal
"""
from typing import Sequence, List, Tuple, Iterable


def get_all_subclasses(cls):
    """
    Searches all subclasses of given class.

    :param cls: The base class.
    :type cls: class
    """

    stack = [cls]
    sub = []
    while len(stack):
        base = stack.pop()
        for child in base.__subclasses__():
            if child not in sub:
                sub.append(child)
                stack.append(child)

    return sub


def sub_seq(s1: Sequence, s2: Sequence) -> bool:
    """
    Checks if sequence s1 is subsequence of s2,

    :param s1: First sequence.
    :type s1: Sequence
    :param s2: Second sequence.
    :type s2: Sequence
    :return: True if s1 is subsequence of s2.
    :rtype: bool
    """

    if len(s1) <= len(s2) and \
            any(s1 == s2[offset:offset + len(s1)] for offset in range(0, len(s2) - len(s1) + 1)):
        return True

    return False


def search_sub_seq(s1: Sequence, s2: Sequence) -> List[Tuple[int, int]]:
    """
    Searches all occurrences of sequence s1 in s2,

    :param s1: First sequence.
    :type s1: Sequence
    :param s2: Second sequence.
    :type s2: Sequence
    :return: List of searched spans. Span is a tuple [start, end).
        Empty list maybe return in case when there are no spans found.
    :rtype: List[Tuple[int, int]]
    :raise ValueError: When one of input sequences haves zero len.
    """

    if len(s1) == 0 or len(s2) == 0:
        raise ValueError("Both sequences must have non zero length.")

    if len(s1) <= len(s2):
        res = []
        for offset in range(0, len(s2) - len(s1) + 1):
            end_offset = offset + len(s1)
            if s1 == s2[offset:end_offset]:
                res.append((offset, end_offset))

        return res

    return []


class RoundSequence(object):
    """
    Wrapper for an Sequence that should iterate infinitely in cyclic fashion.
    """

    def __init__(self, i: Sequence):
        """
        Initialization of wrapper.

        :param i: Sequence you want to wrap.
        :type i: Sequence
        """

        self.s = i
        self.i = iter(self.s)

    def __iter__(self):
        return self.i

    def __next__(self, *args, **kwargs):
        try:
            x = next(self.i)
        except StopIteration:
            self.i = iter(self.s)
            x = next(self.i)

        return x


def compare_pos_in_iterables(a: Iterable, b: Iterable) -> bool:
    """
    Positionally invariant compare of two iterables.

    Example of two same iterables:
        [1,2,3]
        [3,2,1]

    Example of two different iterables:
        [1,2,3]
        [1,4,3]

    :param a: First iterable for comparison.
    :type a: Iterable
    :param b: Second iterable for comparison.
    :type b: Iterable
    :return: True considered the same. False otherwise.
    :rtype: bool
    """

    b = list(b)
    try:
        for x in a:
            b.remove(x)
    except ValueError:
        return False
    return len(b) == 0
