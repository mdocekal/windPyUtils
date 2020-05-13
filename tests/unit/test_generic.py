# -*- coding: UTF-8 -*-
""""
Created on 31.01.20

:author:     Martin Dočekal
"""
import unittest
from windpyutils.generic import subSeq, RoundSequence


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


if __name__ == '__main__':
    unittest.main()
