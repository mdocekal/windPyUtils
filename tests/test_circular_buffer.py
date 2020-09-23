# -*- coding: UTF-8 -*-
""""
Created on 23.03.20
Circular buffer tests.

:author:     Martin Dočekal
"""


import unittest

from windpyutils.structures.circular_buffer import CircularBuffer


class TestEntity(unittest.TestCase):
    """
    Unit tests for circular buffer.
    """

    def setUp(self):
        self.empty_3 = CircularBuffer(3)
        self.empty_10 = CircularBuffer(10)
        self.filled_3 = CircularBuffer(3)
        self.filled_3.put("a")
        self.filled_3.put("b")
        self.filled_3.put("c")

    def test_max_size(self):
        """
        Test of the max size.
        """

        with self.assertRaises(AssertionError):
            buffer = CircularBuffer(0)

        with self.assertRaises(AssertionError):
            buffer = CircularBuffer(-1)

        self.assertEqual(self.empty_3.maxSize, 3)
        self.assertEqual(self.empty_10.maxSize, 10)
        self.assertEqual(self.filled_3.maxSize, 3)

    def test_len(self):
        """
        Test of the len method.
        """

        self.assertEqual(len(self.empty_10), 0)

        for i in range(1, 5):
            self.empty_10.put(i)
            self.assertEqual(len(self.empty_10), i)

    def test_len_over(self):
        """
        Test of the len method when we run over the max size.
        """

        for i in range(0, 20):
            self.empty_10.put(i)

        self.assertEqual(len(self.empty_10), 10)

    def test_getitem_out_of(self):
        """
        Test of the get item when reaching out of the buffer.
        """

        with self.assertRaises(IndexError):
            x = self.empty_10[1]

        with self.assertRaises(IndexError):
            x = self.filled_3[-1]

        with self.assertRaises(IndexError):
            x = self.filled_3[3]

    def test_put(self):
        """
        Test of the put method.
        """

        for i in range(10):
            self.empty_10.put(i)
            self.assertEqual(self.empty_10[i], i)

        # over fill
        self.empty_3.put(0)
        self.empty_3.put(1)

        for i in range(2, 20):
            self.empty_3.put(i)
            for j in range(3):
                self.assertEqual(self.empty_3[j], i-2+j, msg="On offset {}. Item from buffer {} does not equal to reference item {}.".format(j, self.empty_3[j], i-2+j))

    def test_clear(self):
        """
        Test of the clear method.
        """
        self.empty_10.clear()
        self.assertEqual(len(self.empty_10), 0)

        self.filled_3.clear()
        self.assertEqual(len(self.filled_3), 0)


if __name__ == '__main__':
    unittest.main()
