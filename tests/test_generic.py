# -*- coding: UTF-8 -*-
""""
Created on 31.01.20

:author:     Martin Dočekal
"""
import itertools
import unittest
from windpyutils.generic import sub_seq, RoundSequence, search_sub_seq, compare_pos_in_iterables


class TestSubSeq(unittest.TestCase):
    """
    Unit test of subSeq method.
    """

    def test_sub_seq(self):
        """
        Test for subSeq.
        """

        self.assertTrue(sub_seq([], []))
        self.assertTrue(sub_seq([], [1, 2, 3]))
        self.assertFalse(sub_seq([1, 2, 3], []))
        self.assertTrue(sub_seq([2], [1, 2, 3]))
        self.assertTrue(sub_seq([2, 3], [1, 2, 3]))
        self.assertTrue(sub_seq(["Machine", "learning"], ["on", "Machine", "learning", "in", "history"]))
        self.assertFalse(sub_seq(["artificial", "learning"], ["on", "Machine", "learning", "in", "history"]))


class TestRoundSequence(unittest.TestCase):
    """
    Unit test of RoundSequence.
    """

    def setUp(self):
        self.data = [1, 2, 3, 4, 5]
        self.r = RoundSequence(self.data)

    def test_basic(self):
        for i, x in enumerate(self.r):
            self.assertEqual(self.data[i % len(self.data)], x)

            if i == len(self.data)*2.5:
                break


class TestSearchSubSeq(unittest.TestCase):
    """
    Unit test of searchSubSeq method.
    """

    def test_search_sub_seq(self):
        """
        Test for searchSubSeq.
        """

        with self.assertRaises(ValueError):
            _ = search_sub_seq([], [])

        with self.assertRaises(ValueError):
            _ = search_sub_seq([], [1, 2, 3])

        with self.assertRaises(ValueError):
            _ = search_sub_seq([1, 2, 3], [])

        self.assertListEqual(search_sub_seq([2], [1, 2, 3]), [(1, 2)])
        self.assertListEqual(search_sub_seq([2, 3], [1, 2, 3]), [(1, 3)])
        self.assertListEqual(search_sub_seq([3, 4], [1, 2, 3]), [])
        self.assertListEqual(search_sub_seq(["Machine", "learning"], ["on", "Machine", "learning", "in", "history"]), [(1, 3)])
        self.assertListEqual(search_sub_seq(["artificial", "learning"], ["on", "Machine", "learning", "in", "history"]), [])


class TestComparePosInIterables(unittest.TestCase):

    def test_same(self):
        self.assertTrue(compare_pos_in_iterables([], []))

        for perm in itertools.permutations([1, 2, 3]):
            self.assertTrue(compare_pos_in_iterables(perm, [1, 2, 3]))
            self.assertTrue(compare_pos_in_iterables([1, 2, 3], perm))

    def test_different(self):
        self.assertFalse(compare_pos_in_iterables([1, 2, 3], [4, 5]))
        self.assertFalse(compare_pos_in_iterables([1, 2, 3], [1, 4, 3]))


if __name__ == '__main__':
    unittest.main()
