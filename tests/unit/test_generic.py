# -*- coding: UTF-8 -*-
""""
Created on 31.01.20

:author:     Martin Dočekal
"""
import unittest
from windutils.generic import subSeq


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


if __name__ == '__main__':
    unittest.main()