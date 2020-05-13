# -*- coding: UTF-8 -*-
""""
Created on 31.01.20
This module contains generic utils

:author:     Martin Dočekal
"""
from typing import Sequence


def getAllSubclasses(cls):
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


def subSeq(s1: Sequence, s2: Sequence) -> bool:
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
