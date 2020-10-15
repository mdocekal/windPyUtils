# -*- coding: UTF-8 -*-
""""
Created on 15.10.20
Module containing attribute drive dictionary.

:author:     Martin Dočekal
"""
import copy
from collections import ValuesView
from typing import Any, KeysView, List, Tuple, ItemsView


class AttributeDrivenDictionary(dict):
    """
    Base class for all classes that want's to act like a dictionary, but with predefined keys that can not be
    changed (values can) and can be accessed like instance variable.

    WARNING: interface may not be compatible with standard dict interface in all cases

    Example of usage:

        class MyDataClass(AttributeDrivenDictionary):
            def __init__(a:str)"
                self.a = a

        m = MyDataClass("hello")
        m.a     # hello
        m["a"]  # hello
    """

    def __setitem__(self, key, value):
        if key not in self.__dict__.keys():
            raise KeyError(key)

        setattr(self, key, value)

    def __getitem__(self, key) -> Any:
        if key not in self.__dict__.keys():
            raise KeyError(key)

        return getattr(self, key)

    def __len__(self) -> int:
        return len(self.__dict__.keys())

    def __delitem__(self, key):
        raise RuntimeError(f"You can not use del on {self.__class__}.")

    def clear(self):
        raise RuntimeError(f"You can not use clear on {self.__class__}.")

    def copy(self) -> "AttributeDrivenDictionary":
        return copy.copy(self)

    def has_key(self, k) -> bool:
        return k in self.__dict__.keys()

    def update(self, *args, **kwargs):

        for a in args:
            if isinstance(a, dict):
                a = a.items()
            for k, v in a:
                if k in self:
                    setattr(self, k, v)

        for k, v in kwargs.items():
            if k in self:
                setattr(self, k, v)

    def keys(self) -> KeysView:
        return self.__dict__.keys()

    def values(self) -> ValuesView:
        return self.__dict__.values()

    def items(self) -> ItemsView:
        return self.__dict__.items()

    def pop(self, *args):
        raise RuntimeError(f"You can not use pop on {self.__class__}.")

    def __eq__(self, dict_) -> bool:
        if isinstance(dict_, AttributeDrivenDictionary):
            dict_ = dict_.__dict__

        return self.__dict__ == dict_

    def __contains__(self, item) -> bool:
        return item in self.__dict__

    def __iter__(self):
        for key in self.__dict__.keys():
            yield key

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        return str(self.__dict__)
