# -*- coding: UTF-8 -*-
"""
Created on 28.04.23

:author:     Martin Dočekal
"""
from unittest import TestCase


from windpyutils.structures.caches import LRUCache, LFUCache


class TestLRUCache(TestCase):

    def setUp(self) -> None:
        self.cache = LRUCache(3)
        self.cache_full = LRUCache(3)
        self.cache_full[1] = "a"
        self.cache_full[2] = "b"
        self.cache_full[3] = "c"

    def test__len__(self):
        self.assertEqual(0, len(self.cache))
        self.assertEqual(3, len(self.cache_full))

    def test__contains__(self):
        self.assertNotIn(1, self.cache)
        self.assertNotIn(2, self.cache)
        self.assertNotIn(3, self.cache)

        self.assertIn(1, self.cache_full)
        self.assertIn(2, self.cache_full)
        self.assertIn(3, self.cache_full)

    def test__getitem__(self):
        with self.assertRaises(KeyError):
            _ = self.cache[1]

        self.assertEqual("a", self.cache_full[1])
        self.assertSequenceEqual([1, 3, 2], list(self.cache_full))
        self.assertEqual("b", self.cache_full[2])
        self.assertSequenceEqual([2, 1, 3], list(self.cache_full))
        self.assertEqual("c", self.cache_full[3])
        self.assertSequenceEqual([3, 2, 1], list(self.cache_full))

    def test__setitem__(self):
        self.cache[1] = "a"
        self.assertSequenceEqual([1], list(self.cache))
        self.cache[2] = "b"
        self.assertSequenceEqual([2, 1], list(self.cache))
        self.cache[3] = "c"
        self.assertSequenceEqual([3, 2, 1], list(self.cache))
        self.cache[4] = "d"
        self.assertSequenceEqual([4, 3, 2], list(self.cache))

        self.cache_full[4] = "d"
        self.assertSequenceEqual([4, 3, 2], list(self.cache_full))

    def test__delitem__(self):
        with self.assertRaises(KeyError):
            del self.cache[1]

        del self.cache_full[1]
        self.assertSequenceEqual([3, 2], list(self.cache_full))
        del self.cache_full[2]
        self.assertSequenceEqual([3], list(self.cache_full))
        del self.cache_full[3]
        self.assertSequenceEqual([], list(self.cache_full))


class TestLFUCache(TestCase):

    def setUp(self) -> None:
        self.cache = LFUCache(3)
        self.cache_full = LFUCache(3)
        self.cache_full[3] = "c"
        self.cache_full[2] = "b"
        self.cache_full[1] = "a"

    def test__len__(self):
        self.assertEqual(0, len(self.cache))
        self.assertEqual(3, len(self.cache_full))

    def test__contains__(self):
        self.assertNotIn(1, self.cache)
        self.assertNotIn(2, self.cache)
        self.assertNotIn(3, self.cache)

        self.assertIn(1, self.cache_full)
        self.assertIn(2, self.cache_full)
        self.assertIn(3, self.cache_full)

    def test__getitem__(self):
        with self.assertRaises(KeyError):
            _ = self.cache[1]

        self.assertSequenceEqual([1, 2, 3], list(self.cache_full))

        self.assertEqual("a", self.cache_full[1])
        self.assertSequenceEqual([2, 3, 1], list(self.cache_full))
        self.assertEqual("b", self.cache_full[2])
        self.assertSequenceEqual([3, 2, 1], list(self.cache_full))
        self.assertEqual("c", self.cache_full[3])
        self.assertSequenceEqual([3, 2, 1], list(self.cache_full))
        self.assertEqual("c", self.cache_full[3])
        self.assertSequenceEqual([2, 1, 3], list(self.cache_full))

    def test__setitem__(self):
        self.cache[1] = "a"
        self.assertSequenceEqual([1], list(self.cache))
        self.cache[2] = "b"
        self.assertSequenceEqual([2, 1], list(self.cache))
        self.cache[3] = "c"
        self.assertSequenceEqual([3, 2, 1], list(self.cache))
        self.cache[4] = "d"
        self.assertSequenceEqual([4, 2, 1], list(self.cache))

        self.cache_full[4] = "d"
        self.assertSequenceEqual([4, 2, 3], list(self.cache_full))

    def test__delitem__(self):
        with self.assertRaises(KeyError):
            del self.cache[1]

        del self.cache_full[1]
        self.assertSequenceEqual([2, 3], list(self.cache_full))
        del self.cache_full[2]
        self.assertSequenceEqual([3], list(self.cache_full))
        del self.cache_full[3]
        self.assertSequenceEqual([], list(self.cache_full))
