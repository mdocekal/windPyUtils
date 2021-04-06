# -*- coding: UTF-8 -*-
""""
Created on 20.11.19
This module contains implementaton of some common design patterns.

:author:     Martin Dočekal
"""
from functools import wraps
from typing import Dict, Callable


class Singleton(type):
    """
    Metaclass for singletons.
    """
    _clsInstances = {}
    """Dict containing instances of all singleton classes."""

    def __call__(cls, *args, **kwargs):
        try:
            return cls._clsInstances[cls]
        except KeyError:
            cls._clsInstances[cls] = super().__call__(*args, **kwargs)
            return cls._clsInstances[cls]


class Observable(object):
    """
    Implementation of observer like design pattern.

    Example Usage:

        class A(Observable):
            def __init__(self):
                super().__init__()

            @Observable.event("STARTS")
            def starts_the_engine(self):
                ...

            @Observable.event("END", True)    #true means that all arguments will be passed to observer
            def end_the_engine(self, data):
                ...

        a=A()
        a.register_observer("STARTS", observer_callback_method)
    """

    @staticmethod
    def event(tag, pass_arguments=False):
        """
        Use this decorator to mark methods that could be observed.
        """
        return Observable._event(tag, pass_arguments)

    @staticmethod
    def _event(tag, pass_arguments=False):
        """
        Use this decorator to mark methods that could be observed.
        """

        def tags_decorator(f):
            @wraps(f)
            def func_wrapper(o, *arg, **karg):
                f(o, *arg, **karg)
                if pass_arguments:
                    o._Observable__notify(tag, *arg, **karg)
                else:
                    o._Observable__notify(tag)

            return func_wrapper

        return tags_decorator

    def __init__(self):
        self.__observers = {}

    @property
    def observers(self):
        """
        Get all observers.
        """

        return self.__observers

    @observers.setter
    def observers(self, observers: Dict[str, Callable]):
        """
        Set new observers.

        :param observers: New observers.
        :type observers:Dict[str,Callable]
        """

        self.__observers = observers

    def clear_observers(self):
        """
        Clears all observers.
        """
        self.__observers = {}

    def register_observer(self, event_tag, observer):
        """
        Register new observer for observable method (_event).

        :param event_tag: The tag that is passed as parameter for _event decorator.
        :type event_tag: str
        :param observer: Method that should be called
        :type observer: Callable
        """

        s = self.__observers.setdefault(event_tag, set())
        s.add(observer)

    def unregister_observer(self, event_tag, observer):
        """
        Unregister observer for observable method (_event).

        :param event_tag: The tag that is passed as parameter for _event decorator.
        :type event_tag: str
        :param observer: Method that should no longer be called
        :type observer: Callable
        """

        try:
            self.__observers[event_tag].remove(observer)
        except KeyError:
            pass

    def __notify(self, event_tag, *arg, **kw):
        """
        Notify all obervers for given method.

        :param event_tag: The tag that is passed as parameter for _event decorator.
        :type event_tag: str
        """
        try:
            for o in self.__observers[event_tag]:
                o(*arg, **kw)
        except KeyError:
            pass
