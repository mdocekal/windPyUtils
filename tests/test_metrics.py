# -*- coding: UTF-8 -*-
""""
Created on 13.02.20
Unit tests for metrics module.

:author:     Martin Dočekal
"""
import unittest

from windpyutils.metrics import mean_squared_error, root_mean_squared_error


class TestMeanSquaredError(unittest.TestCase):
    """
    Unit tests for mean squared error.
    """

    def test_mean_squared_error(self):
        a = [1, 3, -5.3, 3, 0]
        b = [2, 3, 5, -0.5, 1.3]

        self.assertAlmostEqual(mean_squared_error(a, b), 24.206)

        a = [5, 5, 5, 5]
        b = [5, 5, 5, 5]

        self.assertAlmostEqual(mean_squared_error(a, b), 0)


class TestRootMeanSquaredError(unittest.TestCase):
    """
    Unit tests for mean squared error.
    """

    def test_root_mean_squared_error(self):
        a = [1, 3, -5.3, 3, 0]
        b = [2, 3, 5, -0.5, 1.3]

        self.assertAlmostEqual(root_mean_squared_error(a, b), 4.91995934942556)

        a = [5, 5, 5, 5]
        b = [5, 5, 5, 5]

        self.assertAlmostEqual(root_mean_squared_error(a, b), 0)


if __name__ == '__main__':
    unittest.main()
