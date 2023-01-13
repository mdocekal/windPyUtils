# -*- coding: UTF-8 -*-
""""
Created on 31.01.20

:author:     Martin Dočekal
"""
import itertools
import random
import string
import time
import unittest
from typing import Sequence, Tuple, FrozenSet, Set
from unittest import TestCase

from windpyutils.generic import sub_seq, RoundSequence, search_sub_seq, compare_pos_in_iterables, Batcher, BatcherIter, \
    roman_2_int, int_2_roman, sorted_combinations, arg_sort, min_combinations_in_interval, \
    min_combinations_in_interval_iter_sorted, Wrapper


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
        self.assertEqual(990, roman_2_int("CMXC"))
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
        self.assertEqual("CMXC", int_2_roman(990))
        self.assertEqual("XXXIX", int_2_roman(39))
        self.assertEqual("CCXLVI", int_2_roman(246))
        self.assertEqual("DCCLXXXIX", int_2_roman(789))
        self.assertEqual("MMCDXXI", int_2_roman(2421))
        self.assertEqual("CLX", int_2_roman(160))
        self.assertEqual("CCVII", int_2_roman(207))
        self.assertEqual("MIX", int_2_roman(1009))
        self.assertEqual("MLXVI", int_2_roman(1066))


class TestSortedCombinations(TestCase):
    def test_sorted_combinations_with_same_weights(self):
        # it is basically the same as itertools combinations implementation so lets use it as reference
        res = list(sorted_combinations(range(5), lambda x: 1))
        gt = list(itertools.chain.from_iterable(list(itertools.combinations(range(5), k)) for k in range(1, 6)))
        self.assertSequenceEqual(res, gt)

    def test_sorted_combinations_with_weights_according_to_elements_in_combination(self):
        # it is basically the same as itertools combinations implementation so lets use it as reference
        res = list(sorted_combinations(range(5), lambda x: len(x)))
        gt = list(itertools.chain.from_iterable(list(itertools.combinations(range(5), k)) for k in range(1, 6)))
        self.assertSequenceEqual(res, gt)

    def test_sorted_combinations_weights_are_sum(self):
        res = list(sorted_combinations(range(4), lambda x: sum(x)))
        gt = [
            (0,), (1,), (0, 1), (2,), (0, 2), (3,), (0, 3), (1, 2), (0, 1, 2), (1, 3), (0, 1, 3), (2, 3),
            (0, 2, 3), (1, 2, 3), (0, 1, 2, 3)
        ]
        self.assertSequenceEqual(res, gt)

    def test_sorted_combinations_weights_are_sum_yield_key(self):
        res = list(sorted_combinations(range(4), lambda x: sum(x), yield_key=True))
        gt = [
            ((0,), 0), ((1,), 1), ((0, 1), 1), ((2,), 2), ((0, 2), 2), ((3,), 3), ((0, 3), 3), ((1, 2), 3),
            ((0, 1, 2), 3), ((1, 3), 4), ((0, 1, 3), 4), ((2, 3), 5), ((0, 2, 3), 5), ((1, 2, 3), 6), ((0, 1, 2, 3), 6)
        ]
        self.assertSequenceEqual(res, gt)


class TestArgSort(TestCase):
    def test_arg_sort_sorted(self):
        self.assertSequenceEqual([0, 1, 2, 3, 4], arg_sort([50, 100, 200, 300, 400]))

    def test_arg_sort_reversed(self):
        self.assertSequenceEqual([2, 1, 0], arg_sort([8, 5, 2]))

    def test_arg_sort_in_reverse(self):
        self.assertSequenceEqual([0, 1, 2], arg_sort([8, 5, 2], reverse=True))

    def test_arg_sort_general(self):
        self.assertSequenceEqual([1, 3, 4, 2, 0], arg_sort([400, 50, 300, 100, 200]))


class TestMinCombinationsInIntervalIterSorted(TestCase):
    def setUp(self):
        self.ref = min_combinations_in_interval_iter_sorted
        self.f = self.ref

    @staticmethod
    def convert_combs(combs: Sequence[Tuple[Sequence[str], int]]) -> Set[Tuple[FrozenSet[str], int]]:
        return set((frozenset(c[0]), c[1]) for c in combs)

    def check_res(self, ref_combs: Sequence[Tuple[Sequence[str], int]], combs: Sequence[Tuple[Sequence[str], int]]):
        ref_combs = self.convert_combs(ref_combs)
        combs = self.convert_combs(combs)
        self.assertEqual(ref_combs, combs)

    def test_min_combinations_in_interval(self):
        elements = ["1000e", "1e", "100e", "10e"]
        scores = [1000, 1, 100, 10]
        self.check_res([(["1e"], 1)], self.f(elements, scores, 1, 10))
        self.check_res([(["1e"], 1)], self.f(elements, scores, 1, 9999999))
        self.check_res([(["1e", "10e"], 11)], self.f(elements, scores, 11, 101))
        self.check_res([], self.f(elements, scores, 1050, 1070))
        self.check_res([(["1e", "10e", "100e", "1000e"], 1111)], self.f(elements, scores, 1111, 1112))

    def test_single_element(self):
        elements = ["1e", "100e", "10e"]
        scores = [1, 100, 10]
        self.check_res([(["1e", "10e", "100e"], 111)], self.f(elements, scores, 111, 112))
        self.check_res([(["1e"], 1)], self.f(elements, scores, 1, 2))
        self.check_res([(["10e"], 10)], self.f(elements, scores, 10, 11))

    def test_multiple_with_same_score(self):
        elements = ["a", "b", "c"]
        scores = [1, 1, 1]
        self.check_res([(["a"], 1), (["b"], 1), (["c"], 1)], self.f(elements, scores, 1, 2))
        self.check_res([(["a", "b"], 2), (["b", "c"], 2), (["c", "a"], 2)], self.f(elements, scores, 2, 3))
        self.check_res([(["a", "b", "c"], 3)], self.f(elements, scores, 3, 4))


class TestMinCombinationsInInterval(TestMinCombinationsInIntervalIterSorted):
    def setUp(self):
        self.ref = min_combinations_in_interval_iter_sorted
        self.f = min_combinations_in_interval
        self.rand = random.Random(0)

    def test_against_reference(self):
        for _ in range(5):
            for num_ele in [1, 3, 10, 15]:
                elements = [random.choice(string.ascii_letters) for _ in range(num_ele)]
                scores = [self.rand.randint(0, 100) for _ in range(num_ele)]

                num_of_selected = self.rand.randint(1, len(elements))
                # we are doing selection with repetition because we don't care
                selected_scores = sum(random.choice(scores) for _ in range(num_of_selected))

                i_start = selected_scores
                i_end = i_start + self.rand.randint(1, selected_scores)

                #start = time.time()
                ref_combs = self.ref(elements, scores, i_start, i_end)
                #print("ref_combs", time.time() - start)
                #start = time.time()
                combs = self.f(elements, scores, i_start, i_end)
                #print("combs", time.time() - start)
                self.check_res(ref_combs, combs)


class ForWrapping:
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def plus(self, other):
        return self.value + other.value


class TestWrapper(TestCase):

    def setUp(self) -> None:
        self.wrapper = Wrapper(ForWrapping(7))

    def test_value(self):
        self.assertEqual(7, self.wrapper.value)

    def test_get_value(self):
        self.assertEqual(7, self.wrapper.get_value())

    def test_plus(self):
        self.assertEqual(14, self.wrapper.plus(ForWrapping(7)))

    def test_change_wrapped_object(self):
        self.wrapper.wrapped_obj = ForWrapping(8)
        self.assertEqual(8, self.wrapper.value)
        self.assertEqual(8, self.wrapper.get_value())

    def test_missing_attribute(self):
        with self.assertRaises(AttributeError):
            self.wrapper.missing_attribute

    def test_missing_method(self):
        with self.assertRaises(AttributeError):
            self.wrapper.missing_method()


if __name__ == '__main__':
    unittest.main()
