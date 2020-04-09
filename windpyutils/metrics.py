# -*- coding: UTF-8 -*-
""""
Created on 13.02.20
This module contains metrics.

:author:     Martin Dočekal
"""
import math
from typing import Iterable


def meanSquaredError(results: Iterable[float], targets: Iterable[float]) -> float:
    """
    Calculates mean squered error

    :param results: Guessed results.
    :type results: Iterable[float]
    :param targets: Ground truth results.
    :type targets: Iterable[float]
    :return: MSE
    :rtype: float
    """

    sumVal = 0
    cnt = 0

    for r, t in zip(results, targets):
        sumVal += (r-t)**2
        cnt += 1

    return sumVal/cnt


def rootMeanSquaredError(results: Iterable[float], targets: Iterable[float]) -> float:
    """
    Calculates root mean squered error

    :param results: Guessed results.
    :type results: Iterable[float]
    :param targets: Ground truth results.
    :type targets: Iterable[float]
    :return: RMSE
    :rtype: float
    """

    return math.sqrt(meanSquaredError(results, targets))
