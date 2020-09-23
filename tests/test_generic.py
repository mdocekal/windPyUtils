# -*- coding: UTF-8 -*-
""""
Created on 31.01.20

:author:     Martin Dočekal
"""
import unittest
from windpyutils.generic import subSeq, RoundSequence, searchSubSeq


class TestSubSeq(unittest.TestCase):
    """
    Unit test of subSeq method.
    """

    def test_sub_seq(self):
        """
        Test for subSeq.
        """

        self.assertTrue(subSeq([], []))
        self.assertTrue(subSeq([], [1, 2, 3]))
        self.assertFalse(subSeq([1, 2, 3], []))
        self.assertTrue(subSeq([2], [1, 2, 3]))
        self.assertTrue(subSeq([2, 3], [1, 2, 3]))
        self.assertTrue(subSeq(["Machine", "learning"], ["on", "Machine", "learning", "in", "history"]))
        self.assertFalse(subSeq(["artificial", "learning"], ["on", "Machine", "learning", "in", "history"]))


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

    def test_searchSubSeq(self):
        """
        Test for searchSubSeq.
        """

        with self.assertRaises(ValueError):
            _ = searchSubSeq([], [])

        with self.assertRaises(ValueError):
            _ = searchSubSeq([], [1, 2, 3])

        with self.assertRaises(ValueError):
            _ = searchSubSeq([1, 2, 3], [])

        self.assertListEqual(searchSubSeq([2], [1, 2, 3]), [(1, 2)])
        self.assertListEqual(searchSubSeq([2, 3], [1, 2, 3]),  [(1, 3)])
        self.assertListEqual(searchSubSeq([3, 4], [1, 2, 3]), [])
        self.assertListEqual(searchSubSeq(["Machine", "learning"], ["on", "Machine", "learning", "in", "history"]), [(1, 3)])
        self.assertListEqual(searchSubSeq(["artificial", "learning"], ["on", "Machine", "learning", "in", "history"]), [])


if __name__ == '__main__':
    unittest.main()
