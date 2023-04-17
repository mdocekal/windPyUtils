# -*- coding: UTF-8 -*-
""""
Created on 22.03.21
Tests for files module.

:author:     Martin Dočekal
"""
import json
import multiprocessing
import os
import random
import unittest
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from unittest import TestCase

from windpyutils.files import RandomLineAccessFile, MapAccessFile, MemoryMappedRandomLineAccessFile, \
    MutableRandomLineAccessFile, MutableMemoryMappedRandomLineAccessFile, TmpPool, JsonRecord, Record, RecordFile, \
    MemoryMappedRecordFile, MutableRecordFile, MutableMemoryMappedRecordFile, CSVRecord, TSVRecord, FilePool
from windpyutils.parallel.own_proc_pools import FunctorPool, FunctorWorker

path_to_this_script_file = os.path.dirname(os.path.realpath(__file__))
file_with_line_numbers = os.path.join(path_to_this_script_file, "fixtures/file_with_line_numbers.txt")
file_with_mapping = os.path.join(path_to_this_script_file, "fixtures/mapped_file.txt")
file_with_mapping_index = os.path.join(path_to_this_script_file, "fixtures/mapped_file.index")

TMP_DIR = os.path.join(path_to_this_script_file, "tmp")
RES_TMP_FILE = os.path.join(path_to_this_script_file, "tmp/res.txt")


class GetLineFunctorWorker(FunctorWorker):
    def __init__(self, lines):
        super().__init__()
        self.lines = lines

    def __call__(self, i):
        return int(self.lines[i])


class GetRecordWorker(FunctorWorker):
    def __init__(self, records):
        super().__init__()
        self.records = records

    def __call__(self, i):
        return self.records[i]


class TestRandomLineAccessFile(unittest.TestCase):

    def setUp(self) -> None:
        self.lines_file = RandomLineAccessFile(file_with_line_numbers)

    def test_init(self):
        self.assertEqual(self.lines_file.path_to, file_with_line_numbers)
        self.assertIsNone(self.lines_file.file)
        self.assertFalse(self.lines_file.dirty)

    def test_len(self):
        self.assertEqual(len(self.lines_file), 1000)
        self.assertFalse(self.lines_file.dirty)

    def test_get_line_not_opened(self):
        with self.assertRaises(RuntimeError):
            _ = self.lines_file[0]

    def test_seq_iter(self):
        with self.lines_file as lines:
            res = list(lines)
            gt = [str(i) for i in range(1000)]
            self.assertEqual(gt, res)
        self.assertFalse(self.lines_file.dirty)

    def test_get_line_one_by_one_randomly(self):
        indices = [i for i in range(1000)]
        random.shuffle(indices)

        with self.lines_file as lines:
            for i in indices:
                self.assertEqual(int(lines[i]), i)
        self.assertFalse(self.lines_file.dirty)

    def test_get_line_one_by_one_randomly_multiprocessing(self):
        if multiprocessing.cpu_count() <= 1:
            self.skipTest("Skipping test as there is not enough cpus.")
            return

        indices = [i for i in range(1000)]
        random.shuffle(indices)

        with self.lines_file as lines:
            with FunctorPool([GetLineFunctorWorker(lines) for _ in range(multiprocessing.cpu_count())]) as pool:
                for gt, res in zip(indices, pool.imap(indices)):
                    self.assertEqual(gt, res)
        self.assertFalse(self.lines_file.dirty)

    def test_get_range(self):
        indices = [i for i in range(1000)]
        random.shuffle(indices)

        with self.lines_file as lines:
            self.assertListEqual([i for i in range(10, 20)], [int(x) for x in lines[10:20]])
            self.assertListEqual([i for i in range(10, 20, 2)], [int(x) for x in lines[10:20:2]])
            self.assertListEqual([i for i in range(900)], [int(x) for x in lines[:-100]])
        self.assertFalse(self.lines_file.dirty)

    def test_get_from_iterable(self):
        indices = [i for i in range(1000)]
        random.shuffle(indices)

        with self.lines_file as lines:
            self.assertSequenceEqual([10, 15, 20], [int(x) for x in lines[[10, 15, 20]]])
        self.assertFalse(self.lines_file.dirty)


class TestRandomLineAccessFileFromKnownIndex(TestRandomLineAccessFile):
    def setUp(self) -> None:
        offset = 0
        lines_offsets = []
        for i in range(1000):
            lines_offsets.append(offset)
            offset += len(str(i)) + 1
        self.lines_file = RandomLineAccessFile(file_with_line_numbers, lines_offsets)


class TestRandomLineAccessFileFromIndexFile(TestRandomLineAccessFile):
    def setUp(self) -> None:
        self.lines_file = RandomLineAccessFile(file_with_line_numbers, file_with_line_numbers+".index")


class TestMemoryMappedRandomLineAccessFile(TestRandomLineAccessFile):

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
            self.assertFalse(self.lines_file.dirty)
            self.lines_file[0] = "A"
            self.assertTrue(self.lines_file.dirty)
            self.gt[0] = "A"
            self.assertSequenceEqual(self.gt, self.lines_file)

            self.lines_file[2] = "B"
            self.gt[2] = "B"
            self.assertSequenceEqual(self.gt, self.lines_file)
            self.assertTrue(self.lines_file.dirty)

    def test_setitem_invalid_value(self):
        with self.assertRaises(ValueError):
            self.assertFalse(self.lines_file.dirty)
            self.lines_file[0] = 10
            self.assertFalse(self.lines_file.dirty)

    def test_del(self):
        with self.lines_file:
            del self.gt[999]
            del self.lines_file[999]
            self.assertSequenceEqual(self.gt, self.lines_file)
            self.assertTrue(self.lines_file.dirty)
            del self.gt[500]
            del self.lines_file[500]
            self.assertSequenceEqual(self.gt, self.lines_file)
            self.assertTrue(self.lines_file.dirty)
            del self.gt[0]
            del self.lines_file[0]
            self.assertSequenceEqual(self.gt, self.lines_file)
            self.assertTrue(self.lines_file.dirty)

    def test_insert(self):
        with self.lines_file:
            self.gt.insert(10, "A")
            self.lines_file.insert(10, "A")
            self.assertSequenceEqual(self.gt, self.lines_file)
            self.assertTrue(self.lines_file.dirty)

    def test_insert_after(self):
        with self.lines_file:
            self.gt.insert(9999, "A")
            self.lines_file.insert(9999, "A")
            self.assertSequenceEqual(self.gt, self.lines_file)
            self.assertTrue(self.lines_file.dirty)

    def test_insert_before(self):
        with self.lines_file:
            self.gt.insert(-1, "A")
            self.lines_file.insert(-1, "A")
            self.assertSequenceEqual(self.gt, self.lines_file)
            self.assertTrue(self.lines_file.dirty)

    def test_append(self):
        with self.lines_file:
            self.gt.append("A")
            self.lines_file.append("A")
            self.assertSequenceEqual(self.gt, self.lines_file)
            self.assertTrue(self.lines_file.dirty)

    def test_save(self):
        out = StringIO()
        with self.lines_file:
            self.lines_file.save(out)
            self.assertEqual("\n".join(self.gt) + "\n", out.getvalue())
            self.assertFalse(self.lines_file.dirty)

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
            self.assertTrue(self.lines_file.dirty)

    def test_save_with_diff_end(self):
        out = StringIO()
        with self.lines_file:
            self.gt[100] = "A"
            self.lines_file[100] = "A"
            self.lines_file.save(out, "\t")
            self.assertEqual("\t".join(self.gt) + "\t", out.getvalue())
            self.assertTrue(self.lines_file.dirty)


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

    def test_with_dict_multiprocessing(self):
        if multiprocessing.cpu_count() <= 1:
            self.skipTest("Skipping test as there is not enough cpus.")
            return
        mapped_file = MapAccessFile(file_with_mapping, self.gt_map)

        self.assertEqual(self.gt_map, mapped_file.mapping)
        self.assertEqual(len(mapped_file), 11)

        with mapped_file:
            with FunctorPool([GetLineFunctorWorker(mapped_file) for _ in range(multiprocessing.cpu_count())]) as pool:
                for gt, res in zip(self.gt_map.keys(), pool.imap(self.gt_map.keys())):
                    self.assertEqual(gt, res)

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


class TestTmpPool(TestCase):
    def test_create(self):
        paths = []
        with TmpPool() as pool:
            for _ in range(10):
                paths.append(pool.create())
                self.assertTrue(os.path.isfile(paths[-1]))

            self.assertEqual(10, len(pool))
            self.assertSequenceEqual(paths, list(pool))

        self.assertEqual(0, len(pool))
        self.assertSequenceEqual([], list(pool))

        for p in paths:
            self.assertFalse(os.path.isfile(p))

    def test_create_given_dir(self):
        paths = []
        with TmpPool(TMP_DIR) as pool:
            for _ in range(10):
                paths.append(pool.create())
                self.assertTrue(os.path.isfile(paths[-1]))
                self.assertTrue(str(Path(paths[-1]).parent.resolve()) == TMP_DIR)
        for p in paths:
            self.assertFalse(os.path.isfile(p))

    def test_remove(self):
        with TmpPool() as pool:
            for _ in range(10):
                p = pool.create()
                pool.remove(p)
                self.assertFalse(os.path.isfile(p))

    def test_flush(self):
        paths = []
        with TmpPool() as pool:
            for _ in range(10):
                paths.append(pool.create())
            pool.flush()
            for p in paths:
                self.assertFalse(os.path.isfile(p))


class CreateTmpFileWorker(FunctorWorker):
    def __init__(self, pool: TmpPool):
        super().__init__()
        self.pool = pool

    def __call__(self, inp: None) -> str:
        return self.pool.create()


class TestTmpPoolMultProc(TestCase):
    def test_create(self):
        if multiprocessing.cpu_count() <= 1:
            self.skipTest("Not enough cpus.")
        paths = []

        with TmpPool(multi_proc=True) as pool, \
                FunctorPool([CreateTmpFileWorker(pool) for _ in range(multiprocessing.cpu_count())]) as proc_pool:
            for p in proc_pool.imap(None for _ in range(multiprocessing.cpu_count())):
                paths.append(p)
                self.assertTrue(os.path.isfile(p))

        for p in paths:
            self.assertFalse(os.path.isfile(p))

    def test_remove(self):
        with TmpPool(multi_proc=True) as pool, \
                FunctorPool([CreateTmpFileWorker(pool) for _ in range(multiprocessing.cpu_count())]) as proc_pool:
            for p in proc_pool.imap(None for _ in range(multiprocessing.cpu_count())):
                pool.remove(p)
                self.assertFalse(os.path.isfile(p))

    def test_flush(self):
        paths = []
        with TmpPool(multi_proc=True) as pool, \
                FunctorPool([CreateTmpFileWorker(pool) for _ in range(multiprocessing.cpu_count())]) as proc_pool:
            for p in proc_pool.imap(None for _ in range(multiprocessing.cpu_count())):
                paths.append(p)
            pool.flush()
            for p in paths:
                self.assertFalse(os.path.isfile(p))


@dataclass
class OwnJsonRecord(JsonRecord):
    mass: float
    velocity: float


class TestJsonRecord(unittest.TestCase):
    def test_load(self) -> None:
        r = OwnJsonRecord.load('{"mass":10.2,"velocity":120}')
        self.assertEqual(10.2, r.mass)
        self.assertEqual(120, r.velocity)

    def test_repr(self):
        r = OwnJsonRecord(10.2, 120)
        representation = r.save()
        d = json.loads(representation)
        self.assertEqual({"mass": 10.2, "velocity": 120}, d)
        r = OwnJsonRecord(20.2, 6)
        representation = r.save()
        d = json.loads(representation)
        self.assertEqual({"mass": 20.2, "velocity": 6}, d)


@dataclass
class OwnCSVRecord(CSVRecord):
    mass: float
    velocity: float


class TestCSVRecord(unittest.TestCase):
    def test_load(self) -> None:
        r = OwnCSVRecord.load('10.2,120')
        self.assertEqual(10.2, r.mass)
        self.assertEqual(120, r.velocity)

    def test_repr(self):
        r = OwnCSVRecord(10.2, 120)
        self.assertEqual('10.2,120\r\n', r.save())
        r = OwnTSVRecord(20.2, 6)
        self.assertEqual('20.2\t6\r\n', r.save())


@dataclass
class OwnTSVRecord(TSVRecord):
    mass: float
    velocity: float


class TestTSVRecord(unittest.TestCase):
    def test_load(self) -> None:
        r = OwnTSVRecord.load('10.2\t120')
        self.assertEqual(10.2, r.mass)
        self.assertEqual(120, r.velocity)

    def test_repr(self):
        r = OwnTSVRecord(10.2, 120)
        self.assertEqual('10.2\t120\r\n', r.save())
        r = OwnTSVRecord(20.2, 6)
        self.assertEqual('20.2\t6\r\n', r.save())


@dataclass
class IntRecord(Record):
    num: int

    @classmethod
    def load(cls, s: str) -> "Record":
        return cls(int(s))

    def save(self) -> str:
        return str(self.num)


class TestRecordFile(unittest.TestCase):

    def setUp(self) -> None:
        self.record_file = RecordFile(file_with_line_numbers, IntRecord)

    def test_init(self):
        self.assertEqual(self.record_file.path_to, file_with_line_numbers)
        self.assertIsNone(self.record_file.file)
        self.assertTrue(self.record_file.dirty)

    def test_len(self):
        self.assertEqual(len(self.record_file), 1000)
        self.assertTrue(self.record_file.dirty)

    def test_get_line_not_opened(self):
        with self.assertRaises(RuntimeError):
            _ = self.record_file[0]

    def test_seq_iter(self):
        with self.record_file as lines:
            res = list(lines)
            gt = [IntRecord(i) for i in range(1000)]
            self.assertSequenceEqual(gt, res)
        self.assertTrue(self.record_file.dirty)

    def test_get_line_one_by_one_randomly(self):
        indices = [i for i in range(1000)]
        random.shuffle(indices)

        with self.record_file as lines:
            for i in indices:
                self.assertEqual(IntRecord(i), lines[i])
        self.assertTrue(self.record_file.dirty)

    def test_get_line_one_by_one_randomly_multiprocessing(self):
        if multiprocessing.cpu_count() <= 1:
            self.skipTest("Skipping test as there is not enough cpus.")
            return

        indices = [i for i in range(1000)]
        random.shuffle(indices)

        with self.record_file as records:
            with FunctorPool([GetRecordWorker(records) for _ in range(multiprocessing.cpu_count())]) as pool:
                for gt, res in zip(indices, pool.imap(indices)):
                    self.assertEqual(IntRecord(gt), res)
        self.assertTrue(self.record_file.dirty)

    def test_get_range(self):
        indices = [i for i in range(1000)]
        random.shuffle(indices)

        with self.record_file as lines:
            r = lines[10:20]
            self.assertSequenceEqual([IntRecord(i) for i in range(10, 20)], r)
            self.assertSequenceEqual([IntRecord(i) for i in range(10, 20, 2)], lines[10:20:2])
            self.assertSequenceEqual([IntRecord(i) for i in range(900)], lines[:-100])
        self.assertTrue(self.record_file.dirty)

    def test_get_from_iterable(self):
        indices = [i for i in range(1000)]
        random.shuffle(indices)

        with self.record_file as lines:
            self.assertSequenceEqual([IntRecord(10), IntRecord(15), IntRecord(20)], lines[[10, 15, 20]])
        self.assertTrue(self.record_file.dirty)


class TestRecordFileFromKnownIndex(TestRecordFile):
    def setUp(self) -> None:
        offset = 0
        lines_offsets = []
        for i in range(1000):
            lines_offsets.append(offset)
            offset += len(str(i)) + 1
        self.record_file = RecordFile(file_with_line_numbers, IntRecord, lines_offsets)


class TestMemoryMappedRecordFile(TestRecordFile):

    def setUp(self) -> None:
        self.record_file = MemoryMappedRecordFile(file_with_line_numbers, IntRecord)


class TestMutableRecordFile(TestRecordFile):
    def setUp(self) -> None:
        self.record_file = MutableRecordFile[IntRecord](file_with_line_numbers, IntRecord)
        self.gt = list(IntRecord(x) for x in range(1000))

    def tearDown(self) -> None:
        if os.path.isfile(RES_TMP_FILE):
            os.remove(RES_TMP_FILE)

    def test_setitem(self):
        with self.record_file:
            self.assertTrue(self.record_file.dirty)
            self.record_file[0] = IntRecord(9999)
            self.assertTrue(self.record_file.dirty)
            self.gt[0] = IntRecord(9999)
            self.assertSequenceEqual(self.gt, self.record_file)

            self.record_file[2] = IntRecord(99999)
            self.gt[2] = IntRecord(99999)
            self.assertSequenceEqual(self.gt, self.record_file)
            self.assertTrue(self.record_file.dirty)

    def test_setitem_invalid_value(self):
        with self.assertRaises(ValueError):
            self.assertTrue(self.record_file.dirty)
            self.record_file[0] = 10
            self.assertTrue(self.record_file.dirty)

    def test_del(self):
        with self.record_file:
            del self.gt[999]
            del self.record_file[999]
            self.assertSequenceEqual(self.gt, self.record_file)
            self.assertTrue(self.record_file.dirty)
            del self.gt[500]
            del self.record_file[500]
            self.assertSequenceEqual(self.gt, self.record_file)
            self.assertTrue(self.record_file.dirty)
            del self.gt[0]
            del self.record_file[0]
            self.assertSequenceEqual(self.gt, self.record_file)
            self.assertTrue(self.record_file.dirty)

    def test_insert(self):
        with self.record_file:
            self.gt.insert(10, IntRecord(99999))
            self.record_file.insert(10, IntRecord(99999))
            self.assertSequenceEqual(self.gt, self.record_file)
            self.assertTrue(self.record_file.dirty)

    def test_insert_after(self):
        with self.record_file:
            self.gt.insert(9999, IntRecord(99999))
            self.record_file.insert(9999, IntRecord(99999))
            self.assertSequenceEqual(self.gt, self.record_file)
            self.assertTrue(self.record_file.dirty)

    def test_insert_before(self):
        with self.record_file:
            self.gt.insert(-1, IntRecord(99999))
            self.record_file.insert(-1, IntRecord(99999))
            self.assertSequenceEqual(self.gt, self.record_file)
            self.assertTrue(self.record_file.dirty)

    def test_append(self):
        with self.record_file:
            self.gt.append(IntRecord(99999))
            self.record_file.append(IntRecord(99999))
            self.assertSequenceEqual(self.gt, self.record_file)
            self.assertTrue(self.record_file.dirty)

    def test_save(self):
        out = StringIO()
        with self.record_file:
            self.record_file.save(out)
            self.assertEqual("\n".join(str(x.num) for x in self.gt) + "\n", out.getvalue())
            self.assertTrue(self.record_file.dirty)

    def test_save_path(self):
        with self.record_file:
            self.record_file.save(RES_TMP_FILE)

        with open(RES_TMP_FILE, "r") as out:
            self.assertEqual("\n".join(str(x.num) for x in self.gt) + "\n", out.read())

    def test_modified_save(self):
        out = StringIO()
        with self.record_file:
            self.gt[100] = IntRecord(99999)
            self.record_file[100] = IntRecord(99999)
            self.record_file.save(out)
            self.assertEqual("\n".join(str(x.num) for x in self.gt) + "\n", out.getvalue())
            self.assertTrue(self.record_file.dirty)

    def test_save_with_diff_end(self):
        out = StringIO()
        with self.record_file:
            self.gt[100] = IntRecord(99999)
            self.record_file[100] = IntRecord(99999)
            self.record_file.save(out, "\t")
            self.assertEqual("\t".join(str(x.num) for x in self.gt) + "\t", out.getvalue())
            self.assertTrue(self.record_file.dirty)


class TestMutableMemoryMappedRecordFile(TestMutableRandomLineAccessFile):

    def setUp(self) -> None:
        super().setUp()
        self.record_file = MutableMemoryMappedRecordFile(file_with_line_numbers, IntRecord)


class TestFilePool(TestCase):
    def setUp(self) -> None:
        fixtures_path = Path(path_to_this_script_file) / "fixtures"
        self.paths_to_files = [str(fixtures_path / "file_1.txt"), str(fixtures_path / "file_2.txt"),
                               str(fixtures_path / "file_3.txt")]
        self.pool = FilePool(self.paths_to_files)

    def test_len(self):
        with self.assertRaises(RuntimeError):
            len(self.pool)

        with self.pool:
            self.assertEqual(3, len(self.pool))

    def test_iter(self):
        with self.assertRaises(RuntimeError):
            iter(self.pool)
        with self.pool:
            self.assertSequenceEqual(self.paths_to_files, list(x for x in self.pool))

    def test__getitem__(self):
        with self.assertRaises(RuntimeError):
            self.pool[0]
        with self.pool:
            self.assertEqual(self.paths_to_files[0], self.pool[self.paths_to_files[0]].name)
            self.assertEqual(self.paths_to_files[1], self.pool[self.paths_to_files[1]].name)
            self.assertEqual(self.paths_to_files[2], self.pool[self.paths_to_files[2]].name)

    def test_read(self):
        with self.pool:
            self.assertEqual("file 1", self.pool[self.paths_to_files[0]].read().rstrip("\n"))
            self.assertEqual("file 2", self.pool[self.paths_to_files[1]].read().rstrip("\n"))
            self.assertEqual("file 3", self.pool[self.paths_to_files[2]].read().rstrip("\n"))



if __name__ == '__main__':
    unittest.main()
