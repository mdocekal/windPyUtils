# -*- coding: UTF-8 -*-
""""
Created on 22.03.21
Tests for files module.

:author:     Martin Dočekal
"""
import os
import random
import unittest

from windpyutils.files import RandomLineAccessFile


class TestRandomLineAccessFile(unittest.TestCase):
    path_to_this_script_file = os.path.dirname(os.path.realpath(__file__))
    file_with_line_numbers = os.path.join(path_to_this_script_file, "fixtures/file_with_line_numbers.txt")

    def setUp(self) -> None:
        self.lines_file = RandomLineAccessFile(self.file_with_line_numbers)

    def test_init(self):

        self.assertEqual(self.lines_file.path_to, self.file_with_line_numbers)
        self.assertIsNone(self.lines_file.file)

    def test_len(self):
        self.assertEqual(len(self.lines_file), 1000)

    def test_get_line_not_opened(self):

        with self.assertRaises(RuntimeError):
            _ = self.lines_file[0]

    def test_get_line(self):
        indices = [i for i in range(1000)]
        random.shuffle(indices)

        with self.lines_file as lines:
            for i in indices:
                self.assertEqual(int(lines[i]), i)


if __name__ == '__main__':
    unittest.main()
