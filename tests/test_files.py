# -*- coding: UTF-8 -*-
""""
Created on 22.03.21
Tests for files module.

:author:     Martin Dočekal
"""
import os
import random
import unittest
from io import StringIO

from windpyutils.files import RandomLineAccessFile, MapAccessFile, MemoryMappedRandomLineAccessFile, \
    MutableRandomLineAccessFile, MutableMemoryMappedRandomLineAccessFile

path_to_this_script_file = os.path.dirname(os.path.realpath(__file__))
file_with_line_numbers = os.path.join(path_to_this_script_file, "fixtures/file_with_line_numbers.txt")
file_with_mapping = os.path.join(path_to_this_script_file, "fixtures/mapped_file.txt")
file_with_mapping_index = os.path.join(path_to_this_script_file, "fixtures/mapped_file.index")

RES_TMP_FILE = os.path.join(path_to_this_script_file, "tmp/res.txt")


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

    def test_get_line_one_by_one(self):
        indices = [i for i in range(1000)]
        random.shuffle(indices)

        with self.lines_file as lines:
            for i in indices:
                self.assertEqual(int(lines[i]), i)

    def test_get_range(self):
        indices = [i for i in range(1000)]
        random.shuffle(indices)

        with self.lines_file as lines:
            self.assertListEqual([i for i in range(10, 20)],  [int(x) for x in lines[10:20]])
            self.assertListEqual([i for i in range(10, 20, 2)], [int(x) for x in lines[10:20:2]])
            self.assertListEqual([i for i in range(900)], [int(x) for x in lines[:-100]])


class TestRandomLineAccessFileFromKnownIndex(TestRandomLineAccessFile):
    def setUp(self) -> None:
        offset = 0
        lines_offsets = []
        for i in range(1000):
            lines_offsets.append(offset)
            offset += len(str(i))+1
        self.lines_file = RandomLineAccessFile(file_with_line_numbers, lines_offsets)


class TestMemoryMappedRandomLineAccessFileFile(TestRandomLineAccessFile):

    def setUp(self) -> None:
        self.lines_file = MemoryMappedRandomLineAccessFile(file_with_line_numbers)


class TestMutableRandomLineAccessFile(TestRandomLineAccessFile):
    def setUp(self) -> None:
        self.lines_file = MutableRandomLineAccessFile(file_with_line_numbers)
        self.gt = list(str(x) for x in range(1000))

    def tearDown(self) -> None:
        if os.path.isfile(RES_TMP_FILE):
            os.remove(RES_TMP_FILE)

    def test_setitem(self):
        with self.lines_file:
            self.lines_file[0] = "A"
            self.gt[0] = "A"
            self.assertSequenceEqual(self.gt, self.lines_file)

            self.lines_file[2] = "B"
            self.gt[2] = "B"
            self.assertSequenceEqual(self.gt, self.lines_file)

    def test_setitem_invalid_value(self):
        with self.assertRaises(ValueError):
            self.lines_file[0] = 10

    def test_del(self):
        with self.lines_file:
            del self.gt[999]
            del self.lines_file[999]
            self.assertSequenceEqual(self.gt, self.lines_file)

            del self.gt[500]
            del self.lines_file[500]
            self.assertSequenceEqual(self.gt, self.lines_file)

            del self.gt[0]
            del self.lines_file[0]
            self.assertSequenceEqual(self.gt, self.lines_file)

    def test_insert(self):
        with self.lines_file:
            self.gt.insert(10, "A")
            self.lines_file.insert(10, "A")
            self.assertSequenceEqual(self.gt, self.lines_file)

    def test_insert_after(self):
        with self.lines_file:
            self.gt.insert(9999, "A")
            self.lines_file.insert(9999, "A")
            self.assertSequenceEqual(self.gt, self.lines_file)

    def test_insert_before(self):
        with self.lines_file:
            self.gt.insert(-1, "A")
            self.lines_file.insert(-1, "A")
            self.assertSequenceEqual(self.gt, self.lines_file)

    def test_append(self):
        with self.lines_file:
            self.gt.append("A")
            self.lines_file.append("A")
            self.assertSequenceEqual(self.gt, self.lines_file)

    def test_save(self):
        out = StringIO()
        with self.lines_file:
            self.lines_file.save(out)
            self.assertEqual("\n".join(self.gt)+"\n", out.getvalue())

    def test_save_path(self):
        with self.lines_file:
            self.lines_file.save(RES_TMP_FILE)

        with open(RES_TMP_FILE, "r") as out:
            self.assertEqual("\n".join(self.gt) + "\n", out.read())

    def test_modified_save(self):
        out = StringIO()
        with self.lines_file:
            self.gt[100] = "A"
            self.lines_file[100] = "A"
            self.lines_file.save(out)
            self.assertEqual("\n".join(self.gt) + "\n", out.getvalue())

    def test_save_with_diff_end(self):
        out = StringIO()
        with self.lines_file:
            self.gt[100] = "A"
            self.lines_file[100] = "A"
            self.lines_file.save(out, "\t")
            self.assertEqual("\t".join(self.gt) + "\t", out.getvalue())


class TestMutableMemoryMappedRandomLineAccessFile(TestMutableRandomLineAccessFile):

    def setUp(self) -> None:
        super().setUp()
        self.lines_file = MutableMemoryMappedRandomLineAccessFile(file_with_line_numbers)


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


