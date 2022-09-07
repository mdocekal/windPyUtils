# -*- coding: UTF-8 -*-
""""
Created on 06.09.22

:author:     Martin Dočekal
"""
from abc import abstractmethod
from typing import Protocol, TypeVar


CT = TypeVar("CT", bound="Comparable")


class Comparable(Protocol):
    @abstractmethod
    def __lt__(self, other: CT) -> bool: ...



