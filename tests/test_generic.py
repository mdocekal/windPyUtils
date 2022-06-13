# -*- coding: UTF-8 -*-
""""
Created on 31.01.20

:author:     Martin Dočekal
"""
import itertools
import unittest
from windpyutils.generic import sub_seq, RoundSequence, search_sub_seq, compare_pos_in_iterables, Batcher, BatcherIter, \
    roman_2_int, int_2_roman


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


class TestRoman2Int(unittest.TestCase):
    def test_single_letters(self):
        self.assertEqual(1, roman_2_int("I"))
        self.assertEqual(5, roman_2_int("V"))
        self.assertEqual(10, roman_2_int("X"))
        self.assertEqual(50, roman_2_int("L"))
        self.assertEqual(100, roman_2_int("C"))
        self.assertEqual(500, roman_2_int("D"))
        self.assertEqual(1000, roman_2_int("M"))

    def test_multiple_letters(self):
        self.assertEqual(4, roman_2_int("IV"))
        self.assertEqual(4, roman_2_int("IIII"))
        self.assertEqual(39, roman_2_int("XXXIX"))
        self.assertEqual(246, roman_2_int("CCXLVI"))
        self.assertEqual(789, roman_2_int("DCCLXXXIX"))
        self.assertEqual(2421, roman_2_int("MMCDXXI"))
        self.assertEqual(160, roman_2_int("CLX"))
        self.assertEqual(207, roman_2_int("CCVII"))
        self.assertEqual(1009, roman_2_int("MIX"))
        self.assertEqual(1066, roman_2_int("MLXVI"))


class TestInt2Roman(unittest.TestCase):
    def test_single_letters(self):
        self.assertEqual("I", int_2_roman(1))
        self.assertEqual("V", int_2_roman(5))
        self.assertEqual("X", int_2_roman(10))
        self.assertEqual("L", int_2_roman(50))
        self.assertEqual("C", int_2_roman(100))
        self.assertEqual("D", int_2_roman(500))
        self.assertEqual("M", int_2_roman(1000))

    def test_multiple_letters(self):
        self.assertEqual("IV", int_2_roman(4))
        self.assertEqual("XXXIX", int_2_roman(39))
        self.assertEqual("CCXLVI", int_2_roman(246))
        self.assertEqual("DCCLXXXIX", int_2_roman(789))
        self.assertEqual("MMCDXXI", int_2_roman(2421))
        self.assertEqual("CLX", int_2_roman(160))
        self.assertEqual("CCVII", int_2_roman(207))
        self.assertEqual("MIX", int_2_roman(1009))
        self.assertEqual("MLXVI", int_2_roman(1066))


if __name__ == '__main__':
    unittest.main()
