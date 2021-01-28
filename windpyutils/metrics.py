# -*- coding: UTF-8 -*-
""""
Created on 13.02.20
This module contains metrics.

:author:     Martin Dočekal
"""
import math
from typing import Iterable


def mean_squared_error(results: Iterable[float], targets: Iterable[float]) -> float:
    """
    Calculates mean squered error

    :param results: Guessed results.
    :type results: Iterable[float]
    :param targets: Ground truth results.
    :type targets: Iterable[float]
    :return: MSE
    :rtype: float
    """

    sum_val = 0
    cnt = 0

    for r, t in zip(results, targets):
        sum_val += (r-t)**2
        cnt += 1

    return sum_val/cnt


def root_mean_squared_error(results: Iterable[float], targets: Iterable[float]) -> float:
    """
    Calculates root mean squered error

    :param results: Guessed results.
    :type results: Iterable[float]
    :param targets: Ground truth results.
    :type targets: Iterable[float]
    :return: RMSE
    :rtype: float
    """

    return math.sqrt(mean_squared_error(results, targets))
