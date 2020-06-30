# -*- coding: UTF-8 -*-
""""
Created on 30.06.20

Module containing class that stores configuration.

:author:     Martin Dočekal
"""
import ast
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

        with open(pathTo, "r") as f:
            config = ast.literal_eval(f.read())

            if not isinstance(config, dict):
                raise SyntaxError("The configuration must be dict.")

            self.validate(config)

            super().__init__(config)

    def validate(self, config: Dict):
        """
        Validates the loaded configuration.

        :param config: Loaded configuration.
        :type config: Dict
        :raise ValueError: Invalid value for a parameter or missing parameter.
        """

        pass
