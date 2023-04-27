# -*- coding: UTF-8 -*-
"""
Created on 27.04.23

:author:     Martin Dočekal
"""
import multiprocessing
import os
from unittest import TestCase

from windpyutils.parallel.own_proc_pools import FunctorWorker, FunctorPool

from windpyutils.parallel.storage import TextFileStorage

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TMP_DIR = os.path.join(SCRIPT_DIR, "tmp")


class Worker(FunctorWorker):
    def __init__(self, storage: TextFileStorage):
        super().__init__()
        self.storage = storage

    def begin(self):
        self.storage.open()

    def end(self):
        self.storage.close()

    def __call__(self, i):
        self.storage[i] = str(i)
        return i


class TestTextFileStorage(TestCase):
    def tearDown(self) -> None:
        # clear content of tmp folder, but placeholder

        for f in os.listdir(TMP_DIR):
            if f != "placeholder":
                os.remove(os.path.join(TMP_DIR, f))

    def test_read_after_finished(self):
        storage = TextFileStorage(TMP_DIR)
        with FunctorPool([Worker(storage) for _ in range(multiprocessing.cpu_count())]) as p:
            for _ in p.imap(range(10_000)):
                pass

        self.assertTrue(storage.is_contiguous())
        self.assertEqual(len(storage), 10_000)
        storage.reader_only = True
        with storage:
            for i in range(10_000):
                self.assertEqual(storage[i], str(i))
