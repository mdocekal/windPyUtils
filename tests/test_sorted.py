# -*- coding: UTF-8 -*-
""""
Created on 04.07.22

:author:     Martin Dočekal
"""
from unittest import TestCase

from windpyutils.structures.sorted import SortedSet, SortedMap


class TestSortedMap(TestCase):
    def setUp(self) -> None:
        self.empty = SortedMap()
        self.filled = SortedMap({10: "a", 9: "b", 8: "c", 7: "d"})

    def test_init(self):
        self.assertSequenceEqual([], list(self.empty.keys()))
        self.assertSequenceEqual([7, 8, 9, 10], list(self.filled.keys()))

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

        with self.assertRaises(TypeError):
            self.assertFalse(None in self.filled)

    def test_getitem(self):
        self.assertEqual("a", self.filled[10])
        self.assertEqual("d", self.filled[7])
        self.assertEqual("c", self.filled[8])
        self.assertEqual("b", self.filled[9])
        with self.assertRaises(KeyError):
            self.filled[99]
        with self.assertRaises(KeyError):
            self.empty[10]
        with self.assertRaises(TypeError):
            self.filled[None]

    def test_setitem(self):
        self.filled[10] = "z"
        self.assertEqual("z", self.filled[10])
        self.filled[7] = "z"
        self.assertEqual("z", self.filled[7])
        self.filled[8] = "z"
        self.assertEqual("z", self.filled[8])
        self.filled[9] = "z"
        self.assertEqual("z", self.filled[9])
        self.filled[99] = "z"
        self.assertEqual("z", self.filled[99])
        self.empty[10] = "z"
        self.assertEqual("z", self.empty[10])

        with self.assertRaises(TypeError):
            self.empty[None] = "z"
            self.assertEqual("z", self.empty[None])

    def test_delitem(self):
        del self.filled[10]
        self.assertFalse(10 in self.filled)
        del self.filled[7]
        self.assertFalse(7 in self.filled)
        del self.filled[8]
        self.assertFalse(8 in self.filled)
        del self.filled[9]
        self.assertFalse(9 in self.filled)
        with self.assertRaises(KeyError):
            del self.filled[99]
        with self.assertRaises(KeyError):
            del self.empty[10]
        with self.assertRaises(KeyError):
            del self.filled[None]

    def test_iter(self):
        self.assertSequenceEqual([7, 8, 9, 10], list(self.filled))
        self.assertSequenceEqual([], list(self.empty))

    def test_clear(self):
        self.filled.clear()
        self.assertSequenceEqual([], list(self.filled))
        self.empty.clear()
        self.assertSequenceEqual([], list(self.empty))

    def test_keys(self):
        self.assertSequenceEqual([7, 8, 9, 10], list(self.filled.keys()))
        self.assertSequenceEqual([], list(self.empty.keys()))

    def test_values(self):
        self.assertSequenceEqual(["d", "c", "b", "a"], list(self.filled.values()))
        self.assertSequenceEqual([], list(self.empty.values()))

    def test_items(self):
        self.assertSequenceEqual([(7, "d"), (8, "c"), (9, "b"), (10, "a")], list(self.filled.items()))
        self.assertSequenceEqual([], list(self.empty.items()))






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
