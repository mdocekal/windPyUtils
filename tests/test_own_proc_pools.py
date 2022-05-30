# -*- coding: UTF-8 -*-
""""
Created on 04.12.21

:author:     Martin Dočekal
"""
import multiprocessing
import os
import unittest
from multiprocessing.queues import Queue

from windpyutils.parallel.own_proc_pools import FunctorPool, FunctorWorker, T, R


class MockWorker(FunctorWorker):

    def __init__(self):
        super().__init__()
        self.scaler = None
        self.begin_called = multiprocessing.Event()
        self.end_called = multiprocessing.Event()

    def __call__(self, inp: int) -> int:
        return inp*2

    def begin(self):
        self.begin_called.set()

    def end(self):
        self.end_called.set()


class TestFunctorPool(unittest.TestCase):
    def setUp(self) -> None:
        self.workers = [MockWorker() for _ in range(2)]

    def test_init(self):
        if os.cpu_count() > 1:
            for w in self.workers:
                self.assertFalse(w.begin_called.is_set())
                self.assertFalse(w.end_called.is_set())

            with FunctorPool(self.workers) as pool:
                for i, w in enumerate(self.workers):
                    self.assertEqual(i, w.wid)
                    self.assertTrue(isinstance(w.work_queue, Queue))
                    self.assertTrue(isinstance(w.results_queue, Queue))

            for w in self.workers:
                self.assertTrue(w.begin_called.is_set())
                self.assertTrue(w.end_called.is_set())
        else:
            self.skipTest("This test can only be run on the multi cpu device.")

    def test_map(self):
        if os.cpu_count() > 1:
            data = [i for i in range(10000)]
            with FunctorPool(self.workers) as pool:
                results = list(pool.imap(data))
                self.assertListEqual([i * 2 for i in data], results)

            for w in self.workers:
                self.assertTrue(w.begin_called.is_set())
                self.assertTrue(w.end_called.is_set())
        else:
            self.skipTest("This test can only be run on the multi cpu device.")

    def test_until_all_ready(self):
        if os.cpu_count() > 1:
            for w in self.workers:
                self.assertFalse(w.begin_called.is_set())
                self.assertFalse(w.end_called.is_set())
            with FunctorPool(self.workers) as pool:
                for w in self.workers:
                    self.assertFalse(w.begin_called.is_set())
                    self.assertFalse(w.end_called.is_set())

                pool.until_all_ready()
                for w in self.workers:
                    self.assertTrue(w.begin_called.is_set())
                    self.assertFalse(w.end_called.is_set())

            for w in self.workers:
                self.assertTrue(w.begin_called.is_set())
                self.assertTrue(w.end_called.is_set())
        else:
            self.skipTest("This test can only be run on the multi cpu device.")

    def test_map_chunk_size(self):
        if os.cpu_count() > 1:
            data = [i for i in range(10000)]
            with FunctorPool(self.workers) as fm:
                results = list(fm.imap(data, chunk_size=250))
                self.assertListEqual(results, [i * 2 for i in data])

            for w in self.workers:
                self.assertTrue(w.begin_called.is_set())
                self.assertTrue(w.end_called.is_set())
        else:
            self.skipTest("This test can only be run on the multi cpu device.")

    def test_map_chunk_big_size(self):
        if os.cpu_count() > 1:
            data = [i for i in range(10000)]

            with FunctorPool(self.workers) as fm:
                results = list(fm.imap(data, chunk_size=700))
                self.assertListEqual(results, [i * 2 for i in data])

            for w in self.workers:
                self.assertTrue(w.begin_called.is_set())
                self.assertTrue(w.end_called.is_set())
        else:
            self.skipTest("This test can only be run on the multi cpu device.")


if __name__ == '__main__':
    unittest.main()
