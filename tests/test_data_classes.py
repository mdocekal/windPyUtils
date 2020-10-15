# -*- coding: UTF-8 -*-
""""
Created on 15.10.20

:author:     Martin Dočekal
"""

import unittest
from typing import List

from windpyutils.generic import comparePosInIterables
from windpyutils.structures.data_classes import AttributeDrivenDictionary


class MyDataClassAttributeDrivenDictionary(AttributeDrivenDictionary):
    def __init__(self, a: str, b: int, c: List[int]):
        self.a = a
        self.b = b
        self.c = c


class TestAttributeDrivenDictionary(unittest.TestCase):

    def setUp(self) -> None:
        self.m = MyDataClassAttributeDrivenDictionary("hello", 7, [1, 2, 3, 4])

        self.d = {"a": "hello", "b": 7, "c": [1, 2, 3, 4]}

    def test_set_item(self):
        self.m["a"] = "hi"
        self.assertEqual(self.m.a, "hi")

        with self.assertRaises(KeyError):
            self.m["light"] = 299792458

    def test_get_item(self):
        self.assertEqual(self.m["a"], "hello")
        self.assertEqual(self.m["b"], 7)
        self.assertEqual(self.m["c"], [1, 2, 3, 4])

    def test_len(self):
        self.assertEqual(len(self.m), len(self.d))

    def test_delitem(self):
        with self.assertRaises(RuntimeError):
            del self.m["c"]

    def test_clear(self):
        with self.assertRaises(RuntimeError):
            self.m.clear()

    def test_copy(self):
        self.assertEqual(self.m.copy(), self.d)

    def test_has_key(self):
        self.assertTrue(self.m.has_key("a"))
        self.assertTrue(self.m.has_key("b"))
        self.assertTrue(self.m.has_key("c"))

    def test_update_iterable(self):
        self.m.update([("a", "hi"), ("b", 777), ("g", 69)])
        self.assertEqual(self.m.a, "hi")
        self.assertEqual(self.m.b, 777)
        self.assertEqual(self.m.c, [1, 2, 3, 4])

        # the g should be ignored
        with self.assertRaises(AttributeError):
            self.m.g
        with self.assertRaises(KeyError):
            self.m["g"]

    def test_update_dict(self):
        self.m.update({"a": "hi", "b": 777, "g": 69})
        self.assertEqual(self.m.a, "hi")
        self.assertEqual(self.m.b, 777)
        self.assertEqual(self.m.c, [1, 2, 3, 4])

        self.m.update(a="There")
        self.assertEqual(self.m.a, "There")
        self.assertEqual(self.m.b, 777)
        self.assertEqual(self.m.c, [1, 2, 3, 4])

        # the g should be ignored
        with self.assertRaises(AttributeError):
            self.m.g
        with self.assertRaises(KeyError):
            self.m["g"]

    def test_keys(self):
        self.assertEqual(self.m.keys(), self.d.keys())

    def test_values(self):
        comparePosInIterables(self.m.values(), self.d.values())

    def test_items(self):
        comparePosInIterables(self.m.items(), self.d.items())

    def test_pop(self):
        with self.assertRaises(RuntimeError):
            self.m.pop("a")

    def test_eq(self):
        self.assertTrue(self.m == self.d)
        self.assertTrue(self.m == self.m)
        self.assertTrue(self.m == MyDataClassAttributeDrivenDictionary("hello", 7, [1, 2, 3, 4]))

        self.assertFalse(self.m == {"a": "hello"})
        self.assertFalse(self.m == {"t": "hello"})
        self.assertFalse(self.m == {"1": "hello", "2": 7, "3": [1, 2, 3, 4]})
        self.assertFalse(self.m == {"a": "hello", "b": 7, "c": [4, 4, 4, 4]})
        self.assertFalse(self.m == {"a": "hello", "b": 5, "c": [1, 2, 3, 4]})

    def test_contains(self):
        self.assertTrue("a" in self.m)
        self.assertTrue("b" in self.m)
        self.assertTrue("c" in self.m)

        self.assertFalse("l" in self.m)
        self.assertFalse(7 in self.m)

    def test_iter(self):
        keys = []

        for k in self.m:
            keys.append(k)

        self.assertEqual(sorted(keys), ["a", "b", "c"])

    def test_repr(self):
        # as far as i am concerned there can be order differences for the same directories
        # so let's make the comparison on key: value part level
        mSet = set(x.strip() for x in repr(self.m)[1:-1].split(","))
        dSet = set(x.strip() for x in repr(self.d)[1:-1].split(","))
        self.assertEqual(mSet, dSet)

    def test_str(self):
        # as far as i am concerned there can be order differences for the same directories
        # so let's make the comparison on key: value part level
        mSet = set(x.strip() for x in str(self.m)[1:-1].split(","))
        dSet = set(x.strip() for x in str(self.d)[1:-1].split(","))
        self.assertEqual(mSet, dSet)


if __name__ == '__main__':
    unittest.main()
