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
        self.pBuffer = PrintBuffer(self.out)

    def test_init(self):
        self.assertEqual(self.pBuffer.fileOut, self.out)
        self.assertEqual(self.pBuffer.waiting_for, 0)

    def test_len(self):
        self.assertEqual(len(self.pBuffer), 0)
        self.pBuffer.print(1, "B")
        self.assertEqual(len(self.pBuffer), 1)
        self.pBuffer.print(2, "C")
        self.assertEqual(len(self.pBuffer), 2)

        self.pBuffer.print(0, "A")
        self.assertEqual(len(self.pBuffer), 0)

    def test_waitFor(self):
        self.assertEqual(self.pBuffer.waiting_for, 0)
        self.pBuffer.print(1, "B")
        self.assertEqual(self.pBuffer.waiting_for, 0)
        self.pBuffer.print(2, "C")
        self.assertEqual(self.pBuffer.waiting_for, 0)

        self.pBuffer.print(0, "A")
        self.assertEqual(self.pBuffer.waiting_for, 3)

    def test_print_in_order(self):
        self.pBuffer.print(0, "A")
        self.assertEqual(self.out.getvalue(), "A\n")
        self.pBuffer.print(1, "B")
        self.assertEqual(self.out.getvalue(), "A\nB\n")
        self.pBuffer.print(2, "C")
        self.assertEqual(self.out.getvalue(), "A\nB\nC\n")

    def test_print_out_of_order(self):
        self.pBuffer.print(1, "B")
        self.assertEqual(self.out.getvalue(), "")
        self.pBuffer.print(2, "C")
        self.assertEqual(self.out.getvalue(), "")
        self.pBuffer.print(0, "A")
        self.assertEqual(self.out.getvalue(), "A\nB\nC\n")

    def test_flush_empty(self):
        self.pBuffer.flush()
        self.assertEqual(self.out.getvalue(), "")
        self.assertEqual(len(self.pBuffer), 0)
        self.assertEqual(self.pBuffer.waiting_for, 0)

    def test_flush_empty_2(self):
        self.pBuffer.print(0, "A")
        self.pBuffer.print(1, "B")
        self.pBuffer.print(2, "C")

        self.pBuffer.flush()

        self.assertEqual(self.out.getvalue(), "A\nB\nC\n")
        self.assertEqual(self.pBuffer.waiting_for, 3)
        self.assertEqual(len(self.pBuffer), 0)

    def test_flush_non_empty(self):
        self.pBuffer.print(1, "B")
        self.pBuffer.print(2, "C")

        self.pBuffer.flush()

        self.assertEqual(self.out.getvalue(), "B\nC\n")
        self.assertEqual(self.pBuffer.waiting_for, 3)
        self.assertEqual(len(self.pBuffer), 0)

    def test_clear_empty(self):
        self.pBuffer.clear()
        self.assertEqual(self.out.getvalue(), "")
        self.assertEqual(len(self.pBuffer), 0)
        self.assertEqual(self.pBuffer.waiting_for, 0)

    def test_clear_empty_2(self):
        self.pBuffer.print(0, "A")
        self.pBuffer.print(1, "B")
        self.pBuffer.print(2, "C")

        self.pBuffer.clear()

        self.assertEqual(self.out.getvalue(), "A\nB\nC\n")
        self.assertEqual(self.pBuffer.waiting_for, 0)
        self.assertEqual(len(self.pBuffer), 0)

    def test_clear_non_empty(self):
        self.pBuffer.print(1, "B")
        self.pBuffer.print(2, "C")

        self.pBuffer.clear()

        self.assertEqual(self.out.getvalue(), "")
        self.assertEqual(self.pBuffer.waiting_for, 0)
        self.assertEqual(len(self.pBuffer), 0)


if __name__ == '__main__':
    unittest.main()
