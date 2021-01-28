# -*- coding: UTF-8 -*-
""""
Created on 15.10.20
Module containing attribute drive dictionary.

:author:     Martin Dočekal
"""
from keyword import iskeyword


class AttributeDrivenDictionary(dict):
    """
    Base class for all classes that want's to act like a dictionary, but it allows to  access keys like instance variable.

    WARNING: interface may not be compatible with standard dict interface in all cases

    Example of usage:

        class MyDataClass(AttributeDrivenDictionary):
            def __init__(a:str)"
                self.a = a

        m = MyDataClass("hello")
        m.a     # hello
        m["a"]  # hello
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        super().__setitem__(key, value)

    def __setitem__(self, key, value):
        if not isinstance(key, str) or not key.isidentifier() or iskeyword(key) or key == "None":
            # key is in invalid form
            raise KeyError(key)

        super().__setitem__(key, value)

    @property
    def __dict__(self):
        # this is dict so it is mapping object to itself all of it's writable attributes
        return self
