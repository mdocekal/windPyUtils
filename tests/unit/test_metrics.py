# -*- coding: UTF-8 -*-
""""
Created on 13.02.20
Unit tests for metrics module.

:author:     Martin Dočekal
"""
import unittest

from windpyutils.metrics import meanSquaredError, rootMeanSquaredError


class TestMeanSquaredError(unittest.TestCase):
    """
    Unit tests for mean squared error.
    """

    def test_mean_squared_error(self):
        A = [1, 3, -5.3, 3, 0]
        B = [2, 3, 5, -0.5, 1.3]

        self.assertAlmostEqual(meanSquaredError(A, B), 24.206)

        A = [5, 5, 5, 5]
        B = [5, 5, 5, 5]

        self.assertAlmostEqual(meanSquaredError(A, B), 0)


class TestRootMeanSquaredError(unittest.TestCase):
    """
    Unit tests for mean squared error.
    """

    def test_root_mean_squared_error(self):
        A = [1, 3, -5.3, 3, 0]
        B = [2, 3, 5, -0.5, 1.3]

        self.assertAlmostEqual(rootMeanSquaredError(A, B), 4.91995934942556)

        A = [5, 5, 5, 5]
        B = [5, 5, 5, 5]

        self.assertAlmostEqual(rootMeanSquaredError(A, B), 0)


if __name__ == '__main__':
    unittest.main()
