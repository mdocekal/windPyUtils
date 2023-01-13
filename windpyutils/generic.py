# -*- coding: UTF-8 -*-
""""
Created on 31.01.20
This module contains generic utils

:author:     Martin Dočekal
"""
import heapq
import itertools
import math
import bisect
from typing import Sequence, List, Tuple, Iterable, Union, Any, Generator, Callable, TypeVar, Optional

from windpyutils.typing import Comparable


def get_all_subclasses(cls):
    """
    Searches all subclasses of given class.

    :param cls: The base class.
    :type cls: class
    """

    stack = [cls]
    sub = []
    while len(stack):
        base = stack.pop()
        for child in base.__subclasses__():
            if child not in sub:
                sub.append(child)
                stack.append(child)

    return sub


def sub_seq(s1: Sequence, s2: Sequence) -> bool:
    """
    Checks if sequence s1 is subsequence of s2,

    :param s1: First sequence.
    :type s1: Sequence
    :param s2: Second sequence.
    :type s2: Sequence
    :return: True if s1 is subsequence of s2.
    :rtype: bool
    """

    if len(s1) <= len(s2) and \
            any(s1 == s2[offset:offset + len(s1)] for offset in range(0, len(s2) - len(s1) + 1)):
        return True

    return False


def search_sub_seq(s1: Sequence, s2: Sequence) -> List[Tuple[int, int]]:
    """
    Searches all occurrences of sequence s1 in s2,

    :param s1: First sequence.
    :type s1: Sequence
    :param s2: Second sequence.
    :type s2: Sequence
    :return: List of searched spans. Span is a tuple [start, end).
        Empty list maybe return in case when there are no spans found.
    :rtype: List[Tuple[int, int]]
    :raise ValueError: When one of input sequences haves zero len.
    """

    if len(s1) == 0 or len(s2) == 0:
        raise ValueError("Both sequences must have non zero length.")

    if len(s1) <= len(s2):
        res = []
        for offset in range(0, len(s2) - len(s1) + 1):
            end_offset = offset + len(s1)
            if s1 == s2[offset:end_offset]:
                res.append((offset, end_offset))

        return res

    return []


class RoundSequence(object):
    """
    Wrapper for an Sequence that should iterate infinitely in cyclic fashion.
    """

    def __init__(self, i: Sequence):
        """
        Initialization of wrapper.

        :param i: Sequence you want to wrap.
        :type i: Sequence
        """

        self.s = i
        self.i = iter(self.s)

    def __iter__(self):
        return self.i

    def __next__(self, *args, **kwargs):
        try:
            x = next(self.i)
        except StopIteration:
            self.i = iter(self.s)
            x = next(self.i)

        return x


def compare_pos_in_iterables(a: Iterable, b: Iterable) -> bool:
    """
    Positionally invariant compare of two iterables.

    Example of two same iterables:
        [1,2,3]
        [3,2,1]

    Example of two different iterables:
        [1,2,3]
        [1,4,3]

    :param a: First iterable for comparison.
    :type a: Iterable
    :param b: Second iterable for comparison.
    :type b: Iterable
    :return: True considered the same. False otherwise.
    :rtype: bool
    """

    b = list(b)
    try:
        for x in a:
            b.remove(x)
    except ValueError:
        return False
    return len(b) == 0


class Batcher:
    """
    Allows accessing data in batches
    """

    def __init__(self, batchify_data: Union[Sequence[Any], Tuple[Sequence[Any], ...]], batch_size: int):
        """
        Initialization of batcher.

        :param batchify_data: data that should be batchified
            it could be a single sequence or tuple of sequences
            in case it is a tuple of sequences batcher will return a batch for every sequene in tuple
        :param batch_size:
        :raise ValueError: when the batch size is invalid or the sequences are of different length
        """
        if isinstance(batchify_data, tuple) \
                and any(len(x) != len(y) for x, y in zip(batchify_data[:-1], batchify_data[1:])):
            raise ValueError("Sequences are of different length")

        if batch_size <= 0:
            raise ValueError("Batch size must be positive integer.")

        self.data = batchify_data
        self.batch_size = batch_size

    def __len__(self):
        """
        Number of batches.
        """

        samples = len(self.data[0]) if isinstance(self.data, tuple) else len(self.data)
        return math.ceil(samples / self.batch_size)

    def __getitem__(self, item) -> Union[Sequence[Any], Tuple[Sequence[Any], ...]]:
        """
        Get batch on given index.

        :param item: index of a batch
        :return: Batch on given index or, in case the tuple was provided in constructor, tuple with batches.
            One for each data sequence.
        :raise IndexError: on invalid index
        """
        if item >= len(self):
            raise IndexError()

        offset = item * self.batch_size

        if isinstance(self.data, tuple):
            return tuple(x[offset:offset + self.batch_size] for x in self.data)
        else:
            return self.data[offset:offset + self.batch_size]


class BatcherIter:
    """
    Allows batching of iterables
    """

    def __init__(self, batchify_data: Union[Iterable[Any], Tuple[Iterable[Any], ...]], batch_size: int):
        """
        Initialization of batcher.

        :param batchify_data: data that should be batchified
            it could be a single iterable or tuple of iterables
            in case it is a tuple of iterables batcher will return a batch for every iterable in tuple
                the iteration is stopped when the shortest iterator is finished
        :param batch_size:
        :raise ValueError: when the batch size is invalid
        """

        if batch_size <= 0:
            raise ValueError("Batch size must be positive integer.")

        self.data = batchify_data
        self.batch_size = batch_size

    def __iter__(self) -> Generator[Union[List[Any], Tuple[List[Any], ...]], None, None]:
        """
        generates batches

        :return: generator of batches
        """

        if isinstance(self.data, tuple):
            batch = tuple([] for _ in range(len(self.data)))
            for x in zip(*self.data):
                for i, s in enumerate(x):
                    batch[i].append(s)
                if len(batch[0]) == self.batch_size:
                    yield batch
                    batch = tuple([] for _ in range(len(self.data)))

            if len(batch[0]) > 0:
                yield batch

        else:
            batch = []
            for x in self.data:
                batch.append(x)
                if len(batch) == self.batch_size:
                    yield batch
                    batch = []

            if len(batch) > 0:
                yield batch


def roman_2_int(n: str) -> int:
    """
    Converts roman number to integer.

    :param n: roman number
    :return: integer representation
    """

    conv_table = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    c = [conv_table[x] for x in n]
    return sum(-x if i < len(n) - 1 and x < c[i + 1] else x for i, x in enumerate(c))


def int_2_roman(n: int) -> str:
    """
    Converts integer to roman number.

    :param n: integer
    :return: roman number representation
    """

    def gen(remainder):
        for v, r in [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
                     (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]:
            times, remainder = divmod(remainder, v)
            yield r * times
            if remainder == 0:
                break

    return "".join(gen(n))


def arg_sort(elements: Sequence[Comparable], reverse: bool = False) -> List[int]:
    """
    Returns the indices that would sort the sequence.

    :param elements: elements for arg sorting
    :param reverse: True activates descended order
    :return: indices
    """
    return sorted(range(len(elements)), key=lambda x: elements[x], reverse=reverse)


T = TypeVar("T")


def sorted_combinations(elements: Iterable[T], key: Callable[[Tuple[T, ...]], Comparable],
                        yield_key: bool = False) -> Generator[Union[Tuple[T, ...], Tuple[Tuple[T, ...], Comparable]],
                                                              None, None]:
    """
    Generator of all combinations in sorted order.
    It assumes that for a combination c and an element e, holds the following property:
        a + (e, ) >= a
    Thus adding an element to a combination could only make the new combination greater or equal to the original one.

    The time complexity is:
        O(2^n log n)
    as it uses heapq which has O(log n) for push and pop instead of constant.

    :param elements: iterable of elements that you want to combine
    :param key: Function that is used to extract a comparison key from each combination.
    :param yield_key: whether the key should be yielded along with combination, useful e.g. when you want to reuse
        computed score
    :return: generator of combinations in sorted order
    """
    priority_queue = [(key((e,)), 1, (e,), i) for i, e in enumerate(elements)]  # 2. pos. assures sorting by comb len

    heapq.heapify(priority_queue)  # O(n)
    while priority_queue:  # O(2^n)
        sel_key, _, comb, index = heapq.heappop(priority_queue)  # O(log n)
        comb: Tuple[T, ...]

        yield (comb, sel_key) if yield_key else comb

        offset = index + 1
        for i, e in enumerate(elements[offset:]):
            new_comb = comb + (e,)
            heapq.heappush(priority_queue, (key(new_comb), len(new_comb), new_comb, i + offset))  # O(log n)


def min_combinations_in_interval_iter_sorted(elements: Sequence[T], scores: Sequence[int], i_start: int,
                                             i_end: int) -> List[Tuple[List[T], int]]:
    """
    Gives combinations that haves minimal sum of scores in given interval.
    It is using method that iterates through sorted combinations until the interval is not reached and ends when the
    interval is passed or the sum of scores is not minimal.

    :param elements: elements for combinations
    :param scores: score for each element
    :param i_start: start of interval (min score sum)
    :param i_end: end of interval (all score sums must be smaller than this)
    :return: list of all combinations that haves minimal sum of scores, each combination is associated with the
        score sum
    """
    res = []
    for combination_indices, comb_score in sorted_combinations(range(len(elements)),
                                                               lambda x: sum(scores[i] for i in x),
                                                               yield_key=True):
        if i_end <= comb_score or (len(res) > 0 and res[-1][1] < comb_score):
            break

        if i_start <= comb_score < i_end:
            res.append(([elements[i] for i in combination_indices], comb_score))
    return res


def min_combinations_in_interval(elements: Sequence[T], scores: Sequence[int], i_start: int, i_end: int,
                                 act_comb_len: Optional[int] = None, endings=None, endings_intervals=None) \
        -> List[Tuple[List[T], int]]:
    """
    THIS FUNCTION IS STILL WORK IN PROGRESS!
    Gives combinations that haves minimal sum of scores in given interval.

    :param elements: elements for combinations
    :param scores: score for each element
    :param i_start: start of interval (min score sum)
    :param i_end: end of interval (all score sums must be smaller than this)
    :param act_comb_len: actual combination length that is used during recursion
    :param endings: helping structure that haves saved interval endings that is used during recursion
    :param endings_intervals: helping structure, storing intervals for each ending, that is used during recursion
    :return: list of all combinations that haves minimal sum of scores, each combination is associated with the
        score sum
    """
    max_comb_len = len(scores)

    if endings is None or endings_intervals is None:
        sorted_indices = arg_sort(scores)
        elements_new, scores_new = [], []
        for i in sorted_indices:
            scores_new.append(scores[i])
            elements_new.append(elements[i])

        elements, scores = elements_new, scores_new

        min_cum_sum = [0]
        for s in scores:
            min_cum_sum.append(min_cum_sum[-1] + s)

        if i_start > min_cum_sum[-1]:
            # out of maximal sum
            return []

        intervals = []  # stores interval starts/ends as tuple (min, max, remaining_comb_len, ele_index)
        endings = []

        for comb_len in range(max_comb_len):
            for i, s in zip(range(len(scores))[comb_len:], scores[comb_len:]):
                interval_min = s + min_cum_sum[comb_len]
                interval_max = s + sum(scores[i - comb_len:i])
                endings.append(interval_min)
                endings.append(interval_max)

                intervals.append((interval_min, interval_max, comb_len, i))

        endings_tmp = []
        endings_intervals = []
        for e in sorted(set(endings)):
            endings_tmp.append(e)
            endings_intervals.append([])
        endings = endings_tmp
        for interval in intervals:
            start_offset = bisect.bisect_left(endings, interval[0])
            end_offset = bisect.bisect_right(endings, interval[1])
            for i in range(start_offset, end_offset):
                endings_intervals[i].append(interval)

    if act_comb_len == 1:
        # shortcut for single elements
        start_offset = bisect.bisect_left(scores, i_start)
        res = []
        # we need to iterate from the start offset in order to be able to process multiple elements with the same score

        for i in range(start_offset, len(scores)):
            s = scores[i]
            if not (i_start <= s < i_end) or (len(res) != 0 and res[-1][-1] != s):
                break
            res.append(([elements[i]], s))
        return res

    start_end_offset = bisect.bisect_left(endings, i_start)
    res = []
    for interval in endings_intervals[start_end_offset]:
        if interval[0] < i_end:
            # the bisect left search moved us to the end that must be equal or greater than the i_start,
            # but at this end could lie an interval that is not in our range

            if interval[0] == interval[1] and (interval[2] == 0 or interval[2] == interval[3]):
                # interval[2] == 0 or interval[2] == interval[3] to prevent going there when we have multiple elements
                # with the same score
                e_of = interval[3] + 1
                s_of = interval[3] - interval[2]
                comb = (elements[s_of:e_of], interval[0])
                if len(res) == 0 or res[0][1] == interval[0]:
                    res.append(comb)
                elif res[0][1] > interval[0]:
                    # better than previous
                    res = [comb]
            else:
                ele = elements[interval[3]]
                ele_score = scores[interval[3]]
                act_endings = []
                act_endings_intervals = []
                for e, inters in zip(endings, endings_intervals):
                    passing_inter = []
                    for inter in inters:
                        if inter[2] <= interval[2] and inter[3] < interval[3]:
                            passing_inter.append(inter)
                    if len(passing_inter) > 0:
                        act_endings.append(e)
                        act_endings_intervals.append(passing_inter)

                for c_ele, c_score in min_combinations_in_interval(elements[:interval[3]], scores[:interval[3]],
                                                                   i_start - ele_score, i_end - ele_score, interval[2],
                                                                   act_endings, act_endings_intervals):
                    assign_score = ele_score + c_score
                    c_ele.append(ele)
                    comb = (c_ele, assign_score)
                    if len(res) == 0 or res[0][1] == assign_score:
                        res.append(comb)
                    elif res[0][1] > assign_score:
                        # better than previous
                        res = [comb]

    return res


class Wrapper:
    """
    Wraps given object and acts like it.
    """
    def __init__(self, obj: Any):
        """
        :param obj: object to wrap
        """
        self.wrapped_obj = obj

    def __getattr__(self, attr):
        return getattr(self.wrapped_obj, attr)
