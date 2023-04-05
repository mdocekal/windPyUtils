# -*- coding: UTF-8 -*-
""""
Created on 04.07.22

:author:     Martin Dočekal
"""
from unittest import TestCase

from windpyutils.structures.sorted import SortedSet


class TestSortedSet(TestCase):
    def setUp(self) -> None:
        self.empty = SortedSet()
        self.filled = SortedSet([10, 9, 8, 7])

    def test_init(self):
        self.assertSequenceEqual([], list(self.empty))
        self.assertSequenceEqual([7, 8, 9, 10], list(self.filled))
        self.assertSequenceEqual([7, 8, 9, 10], list(SortedSet([10, 10, 9, 9, 8, 8, 7, 7])))

    def test_len(self):
        self.assertEqual(0, len(self.empty))
        self.assertEqual(4, len(self.filled))

    def test_in(self):
        self.assertTrue(10 in self.filled)
        self.assertTrue(7 in self.filled)
        self.assertTrue(8 in self.filled)
        self.assertTrue(9 in self.filled)
        self.assertFalse(99 in self.filled)
        self.assertFalse(10 in self.empty)
        self.assertFalse(None in self.filled)   # test even not comparable
        self.assertFalse("some string" in self.filled)

    def test_add(self):
        self.filled.add(5)
        self.assertSequenceEqual([5, 7, 8, 9, 10], list(self.filled))
        self.filled.add(6)
        self.assertSequenceEqual([5, 6, 7, 8, 9, 10], list(self.filled))
        self.filled.add(11)
        self.assertSequenceEqual([5, 6, 7, 8, 9, 10, 11], list(self.filled))

    def test_discard_middle(self):
        self.filled.discard(9)
        self.assertSequenceEqual([7, 8, 10], list(self.filled))

    def test_discard_left(self):
        self.filled.discard(7)
        self.assertSequenceEqual([8, 9, 10], list(self.filled))

    def test_discard_right(self):
        self.filled.discard(10)
        self.assertSequenceEqual([7, 8, 9], list(self.filled))

    def test_insertions_index(self):
        self.assertEqual((0, False), self.empty.insertions_index(10))
        self.assertEqual((0, False), self.empty.insertions_index(10))
        self.assertEqual((4, False), self.filled.insertions_index(11))
        self.assertEqual((3, True), self.filled.insertions_index(10))
        self.assertEqual((2, True), self.filled.insertions_index(9))
        self.assertEqual((1, True), self.filled.insertions_index(8))
        self.assertEqual((0, True), self.filled.insertions_index(7))
        self.assertEqual((0, False), self.filled.insertions_index(6))
