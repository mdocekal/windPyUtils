# -*- coding: UTF-8 -*-
""""
Created on 31.01.20

:author:     Martin Dočekal
"""
import itertools
import unittest
from windpyutils.generic import sub_seq, RoundSequence, search_sub_seq, compare_pos_in_iterables, Batcher, BatcherIter


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

            if i == len(self.data) * 2.5:
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
        self.assertListEqual(search_sub_seq(["Machine", "learning"], ["on", "Machine", "learning", "in", "history"]),
                             [(1, 3)])
        self.assertListEqual(search_sub_seq(["artificial", "learning"], ["on", "Machine", "learning", "in", "history"]),
                             [])


class TestComparePosInIterables(unittest.TestCase):

    def test_same(self):
        self.assertTrue(compare_pos_in_iterables([], []))

        for perm in itertools.permutations([1, 2, 3]):
            self.assertTrue(compare_pos_in_iterables(perm, [1, 2, 3]))
            self.assertTrue(compare_pos_in_iterables([1, 2, 3], perm))

    def test_different(self):
        self.assertFalse(compare_pos_in_iterables([1, 2, 3], [4, 5]))
        self.assertFalse(compare_pos_in_iterables([1, 2, 3], [1, 4, 3]))


class TestBatcher(unittest.TestCase):

    def test_single_bigger_batch(self):
        batcher = Batcher([1, 2, 3, 4, 5], 10)

        self.assertEqual(1, len(batcher))
        self.assertListEqual([1, 2, 3, 4, 5], batcher[0])
        with self.assertRaises(IndexError):
            _ = batcher[1]

    def test_single_invalid_batch_size(self):
        with self.assertRaises(ValueError):
            Batcher([1, 2, 3, 4, 5], 0)

    def test_single_non_divisible_by_batch_size(self):
        batcher = Batcher([1, 2, 3, 4, 5], 3)

        self.assertEqual(2, len(batcher))
        self.assertListEqual([1, 2, 3], batcher[0])
        self.assertListEqual([4, 5], batcher[1])

        with self.assertRaises(IndexError):
            _ = batcher[2]

    def test_single_divisible_by_batch_size(self):
        batcher = Batcher([1, 2, 3, 4, 5, 6], 3)

        self.assertEqual(2, len(batcher))
        self.assertListEqual([1, 2, 3], batcher[0])
        self.assertListEqual([4, 5, 6], batcher[1])

        with self.assertRaises(IndexError):
            _ = batcher[2]

    def test_multi_with_different_length(self):
        with self.assertRaises(ValueError):
            batcher = Batcher(([1, 2, 3, 4, 5, 6], [1, 2]), 3)

    def test_multi(self):
        batcher = Batcher(([1, 2, 3, 4], ["a", "b", "c", "d"]), 2)

        self.assertEqual(2, len(batcher))

        f, s = batcher[0]
        self.assertListEqual([1, 2], f)
        self.assertListEqual(["a", "b"], s)

        f, s = batcher[1]
        self.assertListEqual([3, 4], f)
        self.assertListEqual(["c", "d"], s)

        with self.assertRaises(IndexError):
            _ = batcher[2]


class TestBatcherIter(unittest.TestCase):

    def test_single_bigger_batch(self):
        batcher = BatcherIter([1, 2, 3, 4, 5], 10)
        self.assertListEqual([[1, 2, 3, 4, 5]], list(batcher))

    def test_single_invalid_batch_size(self):
        with self.assertRaises(ValueError):
            BatcherIter([1, 2, 3, 4, 5], 0)

    def test_single_non_divisible_by_batch_size(self):
        batcher = BatcherIter([1, 2, 3, 4, 5], 3)

        self.assertListEqual([[1, 2, 3], [4, 5]], list(batcher))

    def test_single_divisible_by_batch_size(self):
        batcher = BatcherIter([1, 2, 3, 4, 5, 6], 3)
        self.assertListEqual([[1, 2, 3], [4, 5, 6]], list(batcher))

    def test_multi(self):
        batcher = BatcherIter(([1, 2, 3, 4], ["a", "b", "c", "d"]), 2)

        self.assertListEqual([([1, 2], ["a", "b"]), ([3, 4], ["c", "d"])], list(batcher))


if __name__ == '__main__':
    unittest.main()
