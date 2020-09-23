# -*- coding: UTF-8 -*-
""""
Created on 13.05.20
Unit tests for mocks.

:author:     Martin Dočekal
"""
import unittest

from windpyutils.mocking import MockedRand, MockedRandInt


class TestMockedRand(unittest.TestCase):
    """
    Unit test of MockedRand.
    """

    def test_steps(self):
        m = MockedRand(0.1)

        for t in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.0, 0.1, 0.2]:
            self.assertAlmostEqual(m(), t)

    def test_sequence(self):
        m = MockedRand([0, 0.1, 0.2, 0.3, 0.7, 0.5, 0.6, 0.7, 0.8, 0.9])

        for t in [0, 0.1, 0.2, 0.3, 0.7, 0.5, 0.6, 0.7, 0.8, 0.9]:
            self.assertAlmostEqual(m(), t)


class TestMockedRandInt(unittest.TestCase):
    """
    Unit test of MockedRandInt.
    """

    def test_steps(self):
        m = MockedRandInt(1)

        for t in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
            self.assertEqual(m(), t)

        m = MockedRandInt(2)

        for t in [0, 2, 4, 6, 8, 10, 12]:
            self.assertEqual(m(), t)

    def test_sequence(self):
        m = MockedRandInt([0, 1, 2, 100, 4, 50, 6, 7, 8, 9])

        for t in [0, 1, 2, 100, 4, 50, 6, 7, 8, 9]:
            self.assertEqual(m(), t)


if __name__ == '__main__':
    unittest.main()
