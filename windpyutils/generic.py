# -*- coding: UTF-8 -*-
""""
Created on 31.01.20
This module contains generic utils

:author:     Martin Dočekal
"""
from typing import Sequence


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
