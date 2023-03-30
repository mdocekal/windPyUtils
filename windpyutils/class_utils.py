# -*- coding: UTF-8 -*-
"""
Created on 30.03.23

:author:     Martin Dočekal
"""
import inspect
from typing import TypeVar, Type, List

T = TypeVar("T")


def subclasses(cls_type: Type[T], abstract_ok: bool = False) -> List[Type[T]]:
    """
    Returns all subclasses of given class.

    :param cls_type: parent class
    :param abstract_ok: if True also abstract classes will be returned
    :return: all subclasses of given class
    """
    res = []
    for sub_cls in cls_type.__subclasses__():
        if abstract_ok or not inspect.isabstract(sub_cls):
            res.append(sub_cls)
        res.extend(subclasses(sub_cls, abstract_ok))
    return res


def sub_cls_from_its_name(parent_cls: Type[T], name: str, abstract_ok: bool = False) -> Type[T]:
    """
    Searches all subclasses of given classes (also the class itself) and returns class with given name.

    :param parent_cls: parent class whose subclasses should be searched
    :param name: name of searched subclass
    :param abstract_ok: if True also abstract classes will be returned
    :return: subclass of given name
    :raise: ValueError when name with given subclass doesn't exist
    """

    if name == parent_cls.__name__ and (abstract_ok or not inspect.isabstract(parent_cls)):
        return parent_cls

    for c in subclasses(parent_cls, abstract_ok=abstract_ok):
        if c.__name__ == name:
            return c

    raise ValueError(f"Invalid subclass name {name} for parent class {parent_cls}")