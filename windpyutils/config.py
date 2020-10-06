# -*- coding: UTF-8 -*-
""""
Created on 30.06.20

Module containing class that stores configuration.

:author:     Martin Dočekal
"""
import ast
import os
from typing import Dict


class Config(dict):
    """
    Base config class without validation of input parameters.
    If you want to validate the input override the validate method.

    Loads configuration from the python file containing only single dictionary.
    This dictionary is safely loaded with the ast.literal_eval (https://docs.python.org/3/library/ast.html).
    """

    def __init__(self, pathTo: str):
        """
        Config initialization.

        :param pathTo: Path to .py file with configuration.
        :type pathTo: str
        :raise SyntaxError: Invalid input.
        :raise ValueError: Invalid value for a parameter or missing parameter.
        """
        self._pathTo = pathTo
        with open(pathTo, "r") as f:
            config = ast.literal_eval(f.read())

            if not isinstance(config, dict):
                raise SyntaxError("The configuration must be dict.")

            self.validate(config)

            super().__init__(config)

    def translateFilePath(self, path: str) -> str:
        """
        Translates relative path to the absolute path.
        If the path is already absolute than it returns the original.
        All relative paths are set relatively to this config file.

        :param path: Path for translating.
        :type path: str
        :return: translated path
        :rtype: str
        """
        if not os.path.isabs(path):
            path = os.path.join(os.path.dirname(self._pathTo), path)

        return path

    def validate(self, config: Dict):
        """
        Validates the loaded configuration.

        :param config: Loaded configuration.
        :type config: Dict
        :raise ValueError: Invalid value for a parameter or missing parameter.
        """

        pass
