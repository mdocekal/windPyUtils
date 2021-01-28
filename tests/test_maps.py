# -*- coding: UTF-8 -*-
""""
Created on 09.04.20

:author:     Martin Dočekal
"""
import unittest

from windpyutils.structures.maps import ImmutIntervalMap


class TestImutIntervalMap(unittest.TestCase):
    """
    Tests for ImutIntervalMap
    """

    def test_init(self):
        _ = ImmutIntervalMap({})
        _ = ImmutIntervalMap({(1, 10): 1, (11, 20): "a"})

        with self.assertRaises(KeyError):
            _ = ImmutIntervalMap({(1, 10): 1, (10, 20): "a"})
        with self.assertRaises(KeyError):
            _ = ImmutIntervalMap({(1, 20): 1, (11, 20): "a"})
        with self.assertRaises(KeyError):
            _ = ImmutIntervalMap({(3, 2): 1, (11, 20): "a"})

    def test_len(self):
        self.assertEqual(len(ImmutIntervalMap({})), 0)
        self.assertEqual(len(ImmutIntervalMap({(1, 10): 1, (11, 20): "a"})), 2)

    def test_getItem(self):
        i_map = ImmutIntervalMap({(11, 20): "a", (7, 10): 99})

        self.assertEqual(i_map[7], 99)
        self.assertEqual(i_map[8.5], 99)
        self.assertEqual(i_map[10], 99)
        self.assertEqual(i_map[15], "a")

        with self.assertRaises(KeyError):
            _ = i_map[6.5]

        with self.assertRaises(KeyError):
            _ = i_map[10.5]

        with self.assertRaises(KeyError):
            _ = i_map[21]

    def test_iter(self):
        i_map = ImmutIntervalMap({(11, 20): "a", (7, 10): 99, (100, 110): -10})

        gt = [
            ((7, 10), 99),
            ((11, 20), "a"),
            ((100, 110), -10)
        ]
        for gtIntVal, intVal in zip(gt, i_map):
            # check intervals
            self.assertEqual(gtIntVal[0], intVal[0])

            # check values
            self.assertEqual(gtIntVal[1], intVal[1])

    def test_contains(self):
        i_map = ImmutIntervalMap({(11, 20): "a", (7, 10): 99})

        self.assertTrue(11 in i_map)
        self.assertTrue(15 in i_map)
        self.assertTrue(20 in i_map)
        self.assertTrue(7 in i_map)
        self.assertTrue(8 in i_map)
        self.assertTrue(10 in i_map)

        self.assertFalse(0 in i_map)
        self.assertFalse(10.5 in i_map)
        self.assertFalse(100 in i_map)


if __name__ == '__main__':
    unittest.main()
