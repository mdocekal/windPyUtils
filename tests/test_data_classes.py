# -*- coding: UTF-8 -*-
""""
Created on 15.10.20

:author:     Martin Dočekal
"""
import os
import pickle
import unittest
from typing import List

from windpyutils.generic import compare_pos_in_iterables
from windpyutils.structures.data_classes import AttributeDrivenDictionary


class MyDataClassAttributeDrivenDictionary(AttributeDrivenDictionary):
    def __init__(self, a: str, b: int, c: List[int]):
        self.a = a
        self.b = b
        self.c = c


class TestAttributeDrivenDictionary(unittest.TestCase):
    path_to_this_script_file = os.path.dirname(os.path.realpath(__file__))
    path_to_tmp = os.path.join(path_to_this_script_file, "tmp/")
    path_to_pickle = os.path.join(path_to_this_script_file, "tmp/AttributeDrivenDictionary.pickle")

    def setUp(self) -> None:
        self.m = MyDataClassAttributeDrivenDictionary("hello", 7, [1, 2, 3, 4])
        self.d = {"a": "hello", "b": 7, "c": [1, 2, 3, 4]}

    def tearDown(self) -> None:
        if os.path.exists(self.path_to_pickle):
            os.remove(self.path_to_pickle)

    def test_set_item(self):
        self.m["a"] = "hi"
        self.assertEqual(self.m.a, "hi")
        self.assertEqual(self.m["a"], "hi")

    def test_dict(self):
        self.assertEqual(self.m.__dict__, self.d)

    def test_get_item(self):
        self.assertEqual(self.m["a"], "hello")
        self.assertEqual(self.m["b"], 7)
        self.assertEqual(self.m["c"], [1, 2, 3, 4])

    def test_len(self):
        self.assertEqual(len(self.m), len(self.d))

    def test_delitem(self):
        del self.m["c"]
        with self.assertRaises(KeyError):
            _ = self.m["c"]
        with self.assertRaises(AttributeError):
            _ = self.m.c

        _ = self.m.a
        _ = self.m["a"]

    def test_clear(self):
        self.m.clear()

        with self.assertRaises(KeyError):
            _ = self.m["a"]
        with self.assertRaises(AttributeError):
            _ = self.m.a

    def test_copy(self):
        self.assertEqual(self.m.copy(), self.d)

    def test_update_iterable(self):
        self.m.update([("a", "hi"), ("b", 777), ("g", 69)])
        self.assertEqual(self.m.a, "hi")
        self.assertEqual(self.m.b, 777)
        self.assertEqual(self.m.c, [1, 2, 3, 4])

        # the new ones
        self.assertEqual(self.m.g, 69)
        self.assertEqual(self.m["g"], 69)

    def test_update_dict(self):
        self.m.update({"a": "hi", "b": 777, "g": 69})
        self.assertEqual(self.m.a, "hi")
        self.assertEqual(self.m.b, 777)
        self.assertEqual(self.m.c, [1, 2, 3, 4])
        self.assertEqual(self.m.g, 69)
        self.assertEqual(self.m["g"], 69)

        self.m.update(a="There")
        self.assertEqual(self.m.a, "There")
        self.assertEqual(self.m.b, 777)
        self.assertEqual(self.m.c, [1, 2, 3, 4])
        self.assertEqual(self.m.g, 69)
        self.assertEqual(self.m["g"], 69)

    def test_keys(self):
        self.assertEqual(self.m.keys(), self.d.keys())

    def test_values(self):
        compare_pos_in_iterables(self.m.values(), self.d.values())

    def test_items(self):
        compare_pos_in_iterables(self.m.items(), self.d.items())

    def test_pop(self):
        self.m.pop("a")
        self.assertFalse("a" in self.m)

        with self.assertRaises(AttributeError):
            _ = self.m.a

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
        m_set = set(x.strip() for x in repr(self.m)[1:-1].split(","))
        d_set = set(x.strip() for x in repr(self.d)[1:-1].split(","))
        self.assertEqual(m_set, d_set)

    def test_str(self):
        # as far as i am concerned there can be order differences for the same directories
        # so let's make the comparison on key: value part level
        m_set = set(x.strip() for x in str(self.m)[1:-1].split(","))
        d_set = set(x.strip() for x in str(self.d)[1:-1].split(","))
        self.assertEqual(m_set, d_set)

    def test_pickling(self):
        with open(self.path_to_pickle, "wb") as f:
            pickle.dump(self.m, f)

        with open(self.path_to_pickle, "rb") as f:
            pickled_loaded = pickle.load(f)

            self.assertTrue(isinstance(pickled_loaded, AttributeDrivenDictionary))
            self.assertEqual(pickled_loaded, self.m)


if __name__ == '__main__':
    unittest.main()
