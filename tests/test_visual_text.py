# -*- coding: UTF-8 -*-
""""
Created on 05.02.21
Tests for the text module in visual package.

:author:     Martin Dočekal
"""
import contextlib
import unittest
from io import StringIO

from windpyutils.visual.text import print_histogram, print_buckets_histogram


class TestPrintHistogram(unittest.TestCase):
    def test_default(self):
        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_histogram([("red", 10), ("green", 5), ("blue", 7)])

        self.assertEqual(out.getvalue(),
                         "red   ████████████████████████████████████████ 10\n"
                         "green ████████████████████ 5\n"
                         "blue  ████████████████████████████ 7\n")

    def test_values(self):
        with self.assertRaises(ValueError):
            print_histogram([("red", 10), ("green", -5), ("blue", 7)])

    def test_file(self):
        out = StringIO()
        print_histogram([("red", 10), ("green", 5), ("blue", 7)], file=out)

        self.assertEqual(out.getvalue(),
                         "red   ████████████████████████████████████████ 10\n"
                         "green ████████████████████ 5\n"
                         "blue  ████████████████████████████ 7\n")

    def test_max_width(self):
        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_histogram([("red", 10), ("green", 5), ("blue", 7)], max_width=10)

        self.assertEqual(out.getvalue(),
                         "red   ██████████ 10\n"
                         "green █████ 5\n"
                         "blue  ███████ 7\n")

    def test_bar_char(self):
        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_histogram([("red", 10), ("green", 5), ("blue", 7)], bar_char="-")

        self.assertEqual(out.getvalue(),
                         "red   ---------------------------------------- 10\n"
                         "green -------------------- 5\n"
                         "blue  ---------------------------- 7\n")

        # two charts per bar char

        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_histogram([("red", 10), ("green", 5), ("blue", 7)], bar_char="--")

        self.assertEqual(out.getvalue(),
                         "red   -------------------------------------------------------------------------------- 10\n"
                         "green ---------------------------------------- 5\n"
                         "blue  -------------------------------------------------------- 7\n")

    def test_print_value(self):
        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_histogram([("red", 10), ("green", 5), ("blue", 7)], print_value=False)
        self.assertEqual(out.getvalue(),
                         "red   ████████████████████████████████████████\n"
                         "green ████████████████████\n"
                         "blue  ████████████████████████████\n")


class TestPrintBucketsHistogram(unittest.TestCase):
    def test_default(self):
        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_buckets_histogram({0: 2, 5: 8, 10: 18, 15: 8, 20: 2})

        self.assertEqual(out.getvalue(),
                         "0  ████ 2\n"
                         "5  ██████████████████ 8\n"
                         "10 ████████████████████████████████████████ 18\n"
                         "15 ██████████████████ 8\n"
                         "20 ████ 2\n")

    def test_file(self):
        out = StringIO()
        print_buckets_histogram({0: 2, 5: 8, 10: 18, 15: 8, 20: 2}, file=out)

        self.assertEqual(out.getvalue(),
                         "0  ████ 2\n"
                         "5  ██████████████████ 8\n"
                         "10 ████████████████████████████████████████ 18\n"
                         "15 ██████████████████ 8\n"
                         "20 ████ 2\n")

    def test_max_width(self):
        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_buckets_histogram({0: 2, 5: 8, 10: 18, 15: 8, 20: 2}, max_width=10)

        self.assertEqual(out.getvalue(),
                         "0  █ 2\n"
                         "5  ████ 8\n"
                         "10 ██████████ 18\n"
                         "15 ████ 8\n"
                         "20 █ 2\n")

    def test_bar_char(self):
        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_buckets_histogram({0: 2, 5: 8, 10: 18, 15: 8, 20: 2}, bar_char="-")

        self.assertEqual(out.getvalue(),
                         "0  ---- 2\n"
                         "5  ------------------ 8\n"
                         "10 ---------------------------------------- 18\n"
                         "15 ------------------ 8\n"
                         "20 ---- 2\n")

        # two charts per bar char

        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_buckets_histogram({0: 2, 5: 8, 10: 18, 15: 8, 20: 2}, bar_char="--")

        self.assertEqual(out.getvalue(),
                         "0  -------- 2\n"
                         "5  ------------------------------------ 8\n"
                         "10 -------------------------------------------------------------------------------- 18\n"
                         "15 ------------------------------------ 8\n"
                         "20 -------- 2\n")

    def test_print_value(self):
        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_buckets_histogram({0: 2, 5: 8, 10: 18, 15: 8, 20: 2}, print_value=False)
        self.assertEqual(out.getvalue(),
                         "0  ████\n"
                         "5  ██████████████████\n"
                         "10 ████████████████████████████████████████\n"
                         "15 ██████████████████\n"
                         "20 ████\n")

    def test_buckets(self):
        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_buckets_histogram({0: 2, 5: 8, 10: 18, 15: 8, 20: 2}, buckets=1)

        self.assertEqual(out.getvalue(),
                         "[0,20] ████████████████████████████████████████ 38\n")

        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_buckets_histogram({0: 2, 5: 8, 10: 18, 15: 8, 20: 2}, buckets=5)

        self.assertEqual(out.getvalue(),
                         "[0,4)   ████ 2\n"
                         "[4,8)   ██████████████████ 8\n"
                         "[8,12)  ████████████████████████████████████████ 18\n"
                         "[12,16) ██████████████████ 8\n"
                         "[16,20] ████ 2\n")

        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_buckets_histogram({100: 2, 105: 8, 110: 18, 115: 8, 120: 2}, buckets=5)

        self.assertEqual(out.getvalue(),
                         "[100,104) ████ 2\n"
                         "[104,108) ██████████████████ 8\n"
                         "[108,112) ████████████████████████████████████████ 18\n"
                         "[112,116) ██████████████████ 8\n"
                         "[116,120] ████ 2\n")

        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_buckets_histogram({0: 2}, buckets=5)

        self.assertEqual(out.getvalue(), "0 ████████████████████████████████████████ 2\n")

        with self.assertRaises(AssertionError):
            print_buckets_histogram({0: 2, 5: 8, 10: 18, 15: 8, 20: 2}, buckets=0)

        with self.assertRaises(AssertionError):
            print_buckets_histogram({0: 2, 5: 8, 10: 18, 15: 8, 20: 2}, buckets=-2)

        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_buckets_histogram({0: 1, 2: 1}, buckets=4)

        self.assertEqual(out.getvalue(),
                         "[0,0.5) ████████████████████████████████████████ 1\n"
                         "[0.5,1)  0\n"
                         "[1,1.5)  0\n"
                         "[1.5,2] ████████████████████████████████████████ 1\n")

    def test_bucket_size_int(self):
        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_buckets_histogram({0: 2, 5: 8, 10: 18, 15: 8, 20: 2}, buckets=3, bucket_size_int=True)

        self.assertEqual(out.getvalue(),
                         "[0,7)   ██████████████████████ 10\n"
                         "[7,14)  ████████████████████████████████████████ 18\n"
                         "[14,20] ██████████████████████ 10\n")

        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_buckets_histogram({0: 2, 5: 8, 10: 18, 15: 8, 20.5: 2}, buckets=3, bucket_size_int=True)

        self.assertEqual(out.getvalue(),
                         "[0,7)   ██████████████████████ 10\n"
                         "[7,14)  ████████████████████████████████████████ 18\n"
                         "[14,21] ██████████████████████ 10\n")

        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_buckets_histogram({0: 1, 1: 1, 3: 1}, buckets=10, bucket_size_int=True)

        self.assertEqual(out.getvalue(),
                         "0 ████████████████████████████████████████ 1\n"
                         "1 ████████████████████████████████████████ 1\n"
                         "3 ████████████████████████████████████████ 1\n")

    def test_decimals(self):
        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_buckets_histogram({0: 2, 5: 8, 10: 18, 15: 8, 20.5: 2}, buckets=3)

        self.assertEqual(out.getvalue(),
                         "[0,6.83)     ██████████████████████ 10\n"
                         "[6.83,13.67) ████████████████████████████████████████ 18\n"
                         "[13.67,20.5] ██████████████████████ 10\n")

        out = StringIO()
        with contextlib.redirect_stdout(out):
            print_buckets_histogram({0: 2, 5: 8, 10: 18, 15: 8, 20.5: 2}, buckets=3, decimals=4)

        self.assertEqual(out.getvalue(),
                         "[0,6.8333)       ██████████████████████ 10\n"
                         "[6.8333,13.6667) ████████████████████████████████████████ 18\n"
                         "[13.6667,20.5]   ██████████████████████ 10\n")


if __name__ == '__main__':
    unittest.main()
