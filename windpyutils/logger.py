# -*- coding: UTF-8 -*-
""""
Created on 20.11.19
This module contains implementation of observable singleton logger.

:author:     Martin Dočekal
"""
from .design_patterns import Observable, Singleton


class Logger(Observable, metaclass=Singleton):
    """
    This singleton class is useful for broadcasting logs to observes that registers to
    log method.

    If you want to log something just call Logger().log("something") and all
    observers, registered with Logger().register_observer("LOG", observer_callback_method) method,
    will be called.

    """

    @Observable._event("LOG", True)
    def log(self, txt: str):
        """
        Make a log.

        :param txt: Text of the log.
        :type txt: str
        """
        pass
