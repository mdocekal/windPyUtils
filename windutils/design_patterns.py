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
        except:
            cls._clsInstances[cls] = super().__call__(*args, **kwargs)
            return cls._clsInstances[cls]


class Observable(object):
    """
    Implementation of observer like design pattern.

    Example Usage:

        class A(Observable):
            def __init__(self):
                super().__init__()

            @Observable._event("STARTS")
            def startsTheEngine(self):
                ...

            @Observable._event("END", True)    #true means that all arguments will be passed to observer
            def endTheEngine(self, data):
                ...

        a=A()
        a.registerObserver("STARTS", observerCallbackMethod)
    """

    @staticmethod
    def _event(tag, passArguments=False):
        """
        Use this decorator to mark methods that could be observed.
        """

        def tags_decorator(f):
            @wraps(f)
            def funcWrapper(o, *arg, **karg):
                f(o, *arg, **karg)
                if passArguments:
                    o._Observable__notify(tag, *arg, **karg)
                else:
                    o._Observable__notify(tag)

            return funcWrapper

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

    def clearObservers(self):
        """
        Clears all observers.
        """
        self.__observers = {}

    def registerObserver(self, eventTag, observer):
        """
        Register new observer for observable method (_event).

        :param eventTag: The tag that is passed as parameter for _event decorator.
        :type eventTag: str
        :param observer: Method that should be called
        :type observer: Callable
        """

        s = self.__observers.setdefault(eventTag, set())
        s.add(observer)

    def unregisterObserver(self, eventTag, observer):
        """
        Unregister observer for observable method (_event).

        :param eventTag: The tag that is passed as parameter for _event decorator.
        :type eventTag: str
        :param observer: Method that should no longer be called
        :type observer: Callable
        """

        try:
            self.__observers[eventTag].remove(observer)
        except KeyError:
            pass

    def __notify(self, eventTag, *arg, **kw):
        """
        Notify all obervers for given method.

        :param eventTag: The tag that is passed as parameter for _event decorator.
        :type eventTag: str
        """
        try:
            for o in self.__observers[eventTag]:
                o(*arg, **kw)
        except KeyError:
            pass
