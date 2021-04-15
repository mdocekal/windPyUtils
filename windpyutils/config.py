# -*- coding: UTF-8 -*-
""""
Created on 30.06.20

Module containing class that stores configuration.

:author:     Martin Dočekal
"""
import ast
import os
from pathlib import Path
from typing import Dict


class Config(dict):
    """
    Base config class without validation of input parameters.
    If you want to validate the input override the validate method.

    Loads configuration from the python file containing only single dictionary.
    This dictionary is safely loaded with the ast.literal_eval (https://docs.python.org/3/library/ast.html).
    """

    def __init__(self, path_to: str):
        """
        Config initialization.

        :param path_to: Path to .py file with configuration.
        :type path_to: str
        :raise SyntaxError: Invalid input.
        :raise ValueError: Invalid value for a parameter or missing parameter.
        """
        self._path_to = Path(path_to).absolute()
        with open(path_to, "r") as f:
            config = ast.literal_eval(f.read())

            if not isinstance(config, dict):
                raise SyntaxError("The configuration must be dict.")

            self.validate(config)

            super().__init__(config)

    def translate_file_path(self, path: str) -> str:
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
            path = os.path.join(os.path.dirname(self._path_to), path)

        return path

    def validate(self, config: Dict):
        """
        Validates the loaded configuration.

        :param config: Loaded configuration.
        :type config: Dict
        :raise ValueError: Invalid value for a parameter or missing parameter.
        """

        pass
