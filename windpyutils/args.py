# -*- coding: UTF-8 -*-
""""
Created on 30.06.20
Module with wrapper that makes arguments parsers raising exceptions.

:author:     Martin Dočekal
"""

from argparse import ArgumentParser


class ArgumentParserError(Exception):
    """
    Exceptions for argument parsing.
    """
    pass


class ExceptionsArgumentParser(ArgumentParser):
    """
    Argument parser that uses exceptions for error handling.
    """

    def error(self, message):
        raise ArgumentParserError(message)

