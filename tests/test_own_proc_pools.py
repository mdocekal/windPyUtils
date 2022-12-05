# -*- coding: UTF-8 -*-
""""
Created on 04.12.21

:author:     Martin Dočekal
"""
import multiprocessing
import os
import time
import unittest
import math
from multiprocessing.context import BaseContext
from multiprocessing.queues import Queue
from typing import List, Optional

from windpyutils.parallel.own_proc_pools import FunctorPool, FunctorWorker, BaseFunctorWorker, FunctorWorkerFactory, \
    FactoryFunctorPool

context_fork = multiprocessing.get_context("fork")
context_spawn = multiprocessing.get_context("spawn")
context_forkserver = multiprocessing.get_context("forkserver")


class BaseMockWorker(BaseFunctorWorker):

    def __init__(self, context: BaseContext = multiprocessing.get_context(), max_chunks_per_worker: float = math.inf):
        super().__init__(context, max_chunks_per_worker)
        self.scaler = None
        self.begin_called = context.Event()
        self.end_called = context.Event()

    def __call__(self, inp: int) -> int:
        return inp*2

    def begin(self):
        self.begin_called.set()

    def end(self):
        self.end_called.set()


class MockWorker(FunctorWorker):
    def __init__(self, max_chunks_per_worker: float = math.inf,
                 wait: Optional[float] = None):
        super().__init__(max_chunks_per_worker)
        self.scaler = None
        self.begin_called = multiprocessing.Event()
        self.end_called = multiprocessing.Event()
        self.wait = wait

    def __call__(self, inp: int) -> int:
        if self.wait is not None:
            time.sleep(self.wait)
        return inp*2

    def begin(self):
        self.begin_called.set()

    def end(self):
        self.end_called.set()


class ForkMockWorker(BaseMockWorker, context_fork.Process):
    def __init__(self, max_chunks_per_worker: float = math.inf):
        super().__init__(context_fork, max_chunks_per_worker)


class SpawnMockWorker(BaseMockWorker, context_spawn.Process):
    def __init__(self, max_chunks_per_worker: float = math.inf):
        super().__init__(context_spawn, max_chunks_per_worker)


class ForkServerMockWorker(BaseMockWorker, context_forkserver.Process):
    def __init__(self, max_chunks_per_worker: float = math.inf):
        super().__init__(context_forkserver, max_chunks_per_worker)


class BaseMockWorkerLargeData(BaseFunctorWorker):
    def __init__(self, context: BaseContext = multiprocessing.get_context(), max_chunks_per_worker: float = math.inf):
        super().__init__(context, max_chunks_per_worker)
        self.scaler = None
        self.begin_called = context.Event()
        self.end_called = context.Event()

    def __call__(self, inp: int) -> List[int]:
        return [999999]*9999 + [inp*2]

    def begin(self):
        self.begin_called.set()

    def end(self):
        self.end_called.set()


class MockWorkerLargeData(FunctorWorker):
    def __init__(self, max_chunks_per_worker: float = math.inf, wait: Optional[float] = None):
        super().__init__(max_chunks_per_worker)
        self.scaler = None
        self.begin_called = multiprocessing.Event()
        self.end_called = multiprocessing.Event()
        self.wait = wait

    def __call__(self, inp: int) -> List[int]:
        if self.wait is not None:
            time.sleep(self.wait)
        return [999999] * 9999 + [inp * 2]

    def begin(self):
        self.begin_called.set()

    def end(self):
        self.end_called.set()


class MockFunctorWorkerFactory(FunctorWorkerFactory):

    def __init__(self, worker_cls=MockWorker, max_chunks_per_worker: float = math.inf, wait: Optional[float] = None):
        self.created_workers = []
        self.worker_cls = worker_cls
        self.max_chunks_per_worker = max_chunks_per_worker
        self.wait = wait

    def create(self) -> BaseFunctorWorker:
        w = self.worker_cls(self.max_chunks_per_worker, self.wait)
        self.created_workers.append(w)
        return w


class ForkMockWorkerLargeData(BaseMockWorkerLargeData, context_fork.Process):
    def __init__(self, max_chunks_per_worker: float = math.inf):
        super().__init__(context_fork, max_chunks_per_worker)


class SpawnMockWorkerLargeData(BaseMockWorkerLargeData, context_spawn.Process):
    def __init__(self, max_chunks_per_worker: float = math.inf):
        super().__init__(context_spawn, max_chunks_per_worker)


class ForkServerMockWorkerLargeData(BaseMockWorkerLargeData, context_forkserver.Process):
    def __init__(self, max_chunks_per_worker: float = math.inf):
        super().__init__(context_forkserver, max_chunks_per_worker)


class TestFunctorPool(unittest.TestCase):
    def setUp(self) -> None:
        self.workers = [MockWorker() for _ in range(2)]
        self.context = multiprocessing.get_context()
        self._large_worker_class = MockWorkerLargeData

    def test_init(self):
        if os.cpu_count() > 1:
            for w in self.workers:
                self.assertFalse(w.begin_called.is_set())
                self.assertFalse(w.end_called.is_set())

            with FunctorPool(self.workers, self.context) as pool:
                for i, w in enumerate(self.workers):
                    self.assertEqual(i, w.wid)
                    self.assertTrue(isinstance(w.work_queue, Queue))
                    self.assertTrue(isinstance(w.results_queue, Queue))

            for w in self.workers:
                self.assertTrue(w.begin_called.is_set())
                self.assertTrue(w.end_called.is_set())
        else:
            self.skipTest("This test can only be run on the multi cpu device.")

    def test_imap(self):
        if os.cpu_count() > 1:
            data = [i for i in range(10000)]
            with FunctorPool(self.workers, self.context) as pool:
                results = list(pool.imap(data))

            self.assertListEqual([i * 2 for i in data], results)

            for w in self.workers:
                self.assertTrue(w.begin_called.is_set())
                self.assertTrue(w.end_called.is_set())
        else:
            self.skipTest("This test can only be run on the multi cpu device.")

    def test_imap_large_data(self):
        if os.cpu_count() > 1:
            self.workers = [self._large_worker_class() for _ in range(2)]
            data = [i for i in range(10000)]
            
            with FunctorPool(self.workers, self.context) as pool:
                results = list(x[-1] for x in pool.imap(data))
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
            with FunctorPool(self.workers, self.context) as pool:

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
            with FunctorPool(self.workers, self.context) as fm:
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

            with FunctorPool(self.workers, self.context) as fm:
                results = list(fm.imap(data, chunk_size=700))
                self.assertListEqual(results, [i * 2 for i in data])

            for w in self.workers:
                self.assertTrue(w.begin_called.is_set())
                self.assertTrue(w.end_called.is_set())
        else:
            self.skipTest("This test can only be run on the multi cpu device.")


class TestForkFunctorPool(TestFunctorPool):
    def setUp(self) -> None:
        self.workers = [ForkMockWorker() for _ in range(2)]
        self._large_worker_class = ForkMockWorkerLargeData
        self.context = context_fork


class TestSpawnFunctorPool(TestFunctorPool):
    def setUp(self) -> None:
        self.workers = [SpawnMockWorker() for _ in range(2)]
        self._large_worker_class = SpawnMockWorkerLargeData
        self.context = context_spawn


class TestForkServerFunctorPool(TestFunctorPool):
    def setUp(self) -> None:
        self.workers = [ForkServerMockWorker() for _ in range(2)]
        self._large_worker_class = ForkServerMockWorkerLargeData
        self.context = context_forkserver


class TestFactoryFunctorPool(unittest.TestCase):
    def setUp(self) -> None:
        self.workers = 2
        self.factory = MockFunctorWorkerFactory()
        self.context = multiprocessing.get_context()

    def test_init(self):
        if os.cpu_count() > 1:

            with FactoryFunctorPool(self.workers, self.factory, self.context):
                self.assertEqual(2, len(self.factory.created_workers))
                for i, w in enumerate(self.factory.created_workers):
                    self.assertEqual(i, w.wid)
                    self.assertTrue(isinstance(w.work_queue, Queue))
                    self.assertTrue(isinstance(w.results_queue, Queue))
                    self.assertTrue(isinstance(w.replace_queue, Queue))

            for w in self.factory.created_workers:
                self.assertTrue(w.begin_called.is_set())
                self.assertTrue(w.end_called.is_set())
        else:
            self.skipTest("This test can only be run on the multi cpu device.")

    def test_imap(self):
        if os.cpu_count() > 1:
            data = [i for i in range(10000)]
            with FactoryFunctorPool(self.workers, self.factory, None) as pool:
                results = list(pool.imap(data))

            self.assertListEqual([i * 2 for i in data], results)

            for w in self.factory.created_workers:
                self.assertTrue(w.begin_called.is_set())
                self.assertTrue(w.end_called.is_set())
        else:
            self.skipTest("This test can only be run on the multi cpu device.")

    def test_imap_large_data(self):
        if os.cpu_count() > 1:
            self.factory.worker_cls = MockWorkerLargeData
            data = [i for i in range(10000)]

            with FactoryFunctorPool(self.workers, self.factory, self.context) as pool:
                results = list(x[-1] for x in pool.imap(data))
                self.assertListEqual([i * 2 for i in data], results)

            for w in self.factory.created_workers:
                self.assertTrue(w.begin_called.is_set())
                self.assertTrue(w.end_called.is_set())
        else:
            self.skipTest("This test can only be run on the multi cpu device.")

    def test_map_chunk_size(self):
        if os.cpu_count() > 1:
            data = [i for i in range(10000)]
            with FactoryFunctorPool(self.workers, self.factory, self.context) as fm:
                results = list(fm.imap(data, chunk_size=250))
                self.assertListEqual(results, [i * 2 for i in data])

            for w in self.factory.created_workers:
                self.assertTrue(w.begin_called.is_set())
                self.assertTrue(w.end_called.is_set())
        else:
            self.skipTest("This test can only be run on the multi cpu device.")

    def test_map_chunk_big_size(self):
        if os.cpu_count() > 1:
            data = [i for i in range(10000)]

            with FactoryFunctorPool(self.workers, self.factory, self.context) as fm:
                results = list(fm.imap(data, chunk_size=700))
                self.assertListEqual(results, [i * 2 for i in data])

            for w in self.factory.created_workers:
                self.assertTrue(w.begin_called.is_set())
                self.assertTrue(w.end_called.is_set())
        else:
            self.skipTest("This test can only be run on the multi cpu device.")

    def test_replace(self):
        if os.cpu_count() > 1:
            self.factory.worker_cls = MockWorkerLargeData
            data = [i for i in range(10000)]
            self.factory.max_chunks_per_worker = 10
            self.factory.wait = 0.001
            with FactoryFunctorPool(self.workers, self.factory, self.context) as fm:
                results = list(x[-1] for x in fm.imap(data, 100))
                self.assertListEqual(results, [i * 2 for i in data])

            self.assertGreaterEqual(12, len(self.factory.created_workers))
            self.assertLessEqual(10, len(self.factory.created_workers))
            # it must be in that interval as it is possible that at most two processes will ask for replace at the
            # very end, before the pool is shutdown
            for w in self.factory.created_workers:
                self.assertTrue(w.begin_called.is_set())
                self.assertTrue(w.end_called.is_set())
        else:
            self.skipTest("This test can only be run on the multi cpu device.")


if __name__ == '__main__':
    unittest.main()
