# -*- coding: UTF-8 -*-
""""
Created on 09.04.20

:author:     Martin Dočekal
"""
import unittest
from io import StringIO

from windpyutils.buffers import PrintBuffer


class TestPrintBuffer(unittest.TestCase):
    """
    Tests for PrintBuffer
    """

    def setUp(self) -> None:
        self.out = StringIO()
        self.p_buffer = PrintBuffer(self.out)

    def test_init(self):
        self.assertEqual(self.p_buffer.fileOut, self.out)
        self.assertEqual(self.p_buffer.waiting_for, 0)

    def test_len(self):
        self.assertEqual(len(self.p_buffer), 0)
        self.p_buffer.print(1, "B")
        self.assertEqual(len(self.p_buffer), 1)
        self.p_buffer.print(2, "C")
        self.assertEqual(len(self.p_buffer), 2)

        self.p_buffer.print(0, "A")
        self.assertEqual(len(self.p_buffer), 0)

    def test_waitFor(self):
        self.assertEqual(self.p_buffer.waiting_for, 0)
        self.p_buffer.print(1, "B")
        self.assertEqual(self.p_buffer.waiting_for, 0)
        self.p_buffer.print(2, "C")
        self.assertEqual(self.p_buffer.waiting_for, 0)

        self.p_buffer.print(0, "A")
        self.assertEqual(self.p_buffer.waiting_for, 3)

    def test_print_in_order(self):
        self.p_buffer.print(0, "A")
        self.assertEqual(self.out.getvalue(), "A\n")
        self.p_buffer.print(1, "B")
        self.assertEqual(self.out.getvalue(), "A\nB\n")
        self.p_buffer.print(2, "C")
        self.assertEqual(self.out.getvalue(), "A\nB\nC\n")

    def test_print_out_of_order(self):
        self.p_buffer.print(1, "B")
        self.assertEqual(self.out.getvalue(), "")
        self.p_buffer.print(2, "C")
        self.assertEqual(self.out.getvalue(), "")
        self.p_buffer.print(0, "A")
        self.assertEqual(self.out.getvalue(), "A\nB\nC\n")

    def test_print_end(self):
        p_buffer_end = PrintBuffer(self.out, end="&")
        p_buffer_end.print(0, "A")
        self.assertEqual(self.out.getvalue(), "A&")
        p_buffer_end.print(1, "B")
        self.assertEqual(self.out.getvalue(), "A&B&")

    def test_flush_empty(self):
        self.p_buffer.flush()
        self.assertEqual(self.out.getvalue(), "")
        self.assertEqual(len(self.p_buffer), 0)
        self.assertEqual(self.p_buffer.waiting_for, 0)

    def test_flush_empty_2(self):
        self.p_buffer.print(0, "A")
        self.p_buffer.print(1, "B")
        self.p_buffer.print(2, "C")

        self.p_buffer.flush()

        self.assertEqual(self.out.getvalue(), "A\nB\nC\n")
        self.assertEqual(self.p_buffer.waiting_for, 3)
        self.assertEqual(len(self.p_buffer), 0)

    def test_flush_non_empty(self):
        self.p_buffer.print(1, "B")
        self.p_buffer.print(2, "C")

        self.p_buffer.flush()

        self.assertEqual(self.out.getvalue(), "B\nC\n")
        self.assertEqual(self.p_buffer.waiting_for, 3)
        self.assertEqual(len(self.p_buffer), 0)

    def test_clear_empty(self):
        self.p_buffer.clear()
        self.assertEqual(self.out.getvalue(), "")
        self.assertEqual(len(self.p_buffer), 0)
        self.assertEqual(self.p_buffer.waiting_for, 0)

    def test_clear_empty_2(self):
        self.p_buffer.print(0, "A")
        self.p_buffer.print(1, "B")
        self.p_buffer.print(2, "C")

        self.p_buffer.clear()

        self.assertEqual(self.out.getvalue(), "A\nB\nC\n")
        self.assertEqual(self.p_buffer.waiting_for, 0)
        self.assertEqual(len(self.p_buffer), 0)

    def test_clear_non_empty(self):
        self.p_buffer.print(1, "B")
        self.p_buffer.print(2, "C")

        self.p_buffer.clear()

        self.assertEqual(self.out.getvalue(), "")
        self.assertEqual(self.p_buffer.waiting_for, 0)
        self.assertEqual(len(self.p_buffer), 0)


if __name__ == '__main__':
    unittest.main()
