# -*- coding: UTF-8 -*-
""""
Created on 22.03.21
Tests for files module.

:author:     Martin Dočekal
"""
import os
import random
import unittest

from windpyutils.files import RandomLineAccessFile, MapAccessFile

path_to_this_script_file = os.path.dirname(os.path.realpath(__file__))
file_with_line_numbers = os.path.join(path_to_this_script_file, "fixtures/file_with_line_numbers.txt")
file_with_mapping = os.path.join(path_to_this_script_file, "fixtures/mapped_file.txt")
file_with_mapping_index = os.path.join(path_to_this_script_file, "fixtures/mapped_file.index")


class TestRandomLineAccessFile(unittest.TestCase):

    def setUp(self) -> None:
        self.lines_file = RandomLineAccessFile(file_with_line_numbers)

    def test_init(self):
        self.assertEqual(self.lines_file.path_to, file_with_line_numbers)
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


class TestMapAccessFile(unittest.TestCase):
    def setUp(self) -> None:
        self.gt_map = {
            0: 0,
            1: 2,
            2: 4,
            3: 6,
            4: 8,
            5: 10,
            6: 12,
            7: 14,
            8: 16,
            9: 18,
            10: 20
        }

    def test_load_mapping(self):
        mapping = MapAccessFile.load_mapping(file_with_mapping_index)
        self.assertEqual({str(k): v for k, v in self.gt_map.items()}, mapping)

    def test_load_mapping_key_type_conversion(self):
        mapping = MapAccessFile.load_mapping(file_with_mapping_index, int)
        self.assertEqual(self.gt_map, mapping)

    def test_load_mapping_invalid_file(self):
        with self.assertRaises(Exception):
            mapping = MapAccessFile.load_mapping(file_with_line_numbers)

    def test_with_dict(self):
        mapped_file = MapAccessFile(file_with_mapping, self.gt_map)

        self.assertEqual(self.gt_map, mapped_file.mapping)
        self.assertEqual(len(mapped_file), 11)

        with mapped_file:
            for k in self.gt_map.keys():
                self.assertEqual(str(k), mapped_file[k].rstrip())

    def test_with_file(self):
        mapped_file = MapAccessFile(file_with_mapping, file_with_mapping_index, key_type=int)

        self.assertEqual(self.gt_map, mapped_file.mapping)
        self.assertEqual(len(mapped_file), 11)

        with mapped_file:
            for k in self.gt_map.keys():
                self.assertEqual(k, int(mapped_file[k]))

    def test_get_line_not_opened(self):
        mapped_file = MapAccessFile(file_with_mapping, file_with_mapping_index, key_type=int)
        with self.assertRaises(RuntimeError):
            _ = mapped_file[0]


if __name__ == '__main__':
    unittest.main()


