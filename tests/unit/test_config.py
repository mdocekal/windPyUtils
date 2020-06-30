# -*- coding: UTF-8 -*-
""""
Created on 30.06.20
Test for the config module.

:author:     Martin Dočekal
"""
import os
import unittest
from typing import Dict

from windpyutils.config import Config


class TestConfig(unittest.TestCase):
    pathToThisScriptFile = os.path.dirname(os.path.realpath(__file__))
    valid = os.path.join(pathToThisScriptFile, "fixtures/config.py")

    def test_valid(self):
        config = dict(
            lr=0.01,
            max_len=100,
            groups=["a", "b", "c"],
            cities={
                "Brno": {
                    "schools": ["BUT"]
                },
                "Praha": {
                    "burgers": ["vegan", "cheddar bacon"]
                }
            }
        )

        loaded = Config(self.valid)

        self.assertEqual(config["lr"], loaded["lr"])
        self.assertEqual(config["max_len"], loaded["max_len"])
        self.assertListEqual(config["groups"], loaded["groups"])
        self.assertListEqual(config["cities"]["Brno"]["schools"], loaded["cities"]["Brno"]["schools"])
        self.assertListEqual(config["cities"]["Praha"]["burgers"], loaded["cities"]["Praha"]["burgers"])

    def test_validation(self):

        class ValConfig(Config):
            def validate(self, config: Dict):
                if config["max_len"] > 10:
                    raise ValueError("max_len is too big")

        with self.assertRaises(ValueError):
            ValConfig(self.valid)

        class ValOkConfig(Config):
            def validate(self, config: Dict):
                if config["max_len"] <= 0:
                    raise ValueError("max_len must be positive integer")

        ValOkConfig(self.valid)

    def test_invalid(self):
        with self.assertRaises(SyntaxError):
            Config(os.path.join(self.pathToThisScriptFile, "fixtures/config_invalid.py"))

        with self.assertRaises(SyntaxError):
            Config(os.path.join(self.pathToThisScriptFile, "fixtures/config_invalid_2.py"))


if __name__ == '__main__':
    unittest.main()
