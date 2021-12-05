# -*- coding: UTF-8 -*-
""""
Created on 04.12.21
Contains parallel functor map.

:author:     Martin Dočekal
"""
import multiprocessing
import queue
from multiprocessing import Process, Queue
from typing import TypeVar, Iterable, Generator, Callable

from windpyutils.buffers import Buffer

T = TypeVar('T')
R = TypeVar('R')


class FunctorWorker(Process):
    """
    Functor worker for FunctorMap.
    """

    def __init__(self, pf: Callable[[T], R], work_queue: Queue, results_queue: Queue):
        """
        Initialization of parallel worker.

        :param pf: Function you want to run in data-parallel way.
        :param work_queue: queue that is used for receiving work and stop orders
        :param results_queue: queue that is used for sending results
        """
        super().__init__()
        self.pf = pf
        self._work_queue = work_queue
        self._results_queue = results_queue

    def run(self) -> None:
        """
        Run the process.
        """
        try:
            while True:
                q_item = self._work_queue.get()

                if q_item is None:
                    # all done
                    break

                i, data_list = q_item

                self._results_queue.put((i, [self.pf(x) for x in data_list]))

        finally:
            self._work_queue.close()
            self._results_queue.close()


class FunctorMap:
    """
    A parallel map that uses given function.
    """

    def __init__(self, pf: Callable[[T], R], workers: int = -1):
        """
        Initialization of parallel functor map.

        :param pf: Function you want to run in data-parallel way.
        :param workers: Number of parallel workers.
            Values <=0 will create number of workers that will be same as number of cpus.
        """
        super().__init__()
        if workers <= 0:
            workers = multiprocessing.cpu_count()

        self._work_queue = Queue(workers)
        self._results_queue = Queue()
        self.procs = [
            FunctorWorker(pf=pf, work_queue=self._work_queue, results_queue=self._results_queue) for _ in range(workers)
        ]

    def __enter__(self) -> "FunctorMap":
        for p in self.procs:
            p.daemon = True
            p.start()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        for _ in range(len(self.procs)):
            self._work_queue.put(None)
        for p in self.procs:
            p.join()

    def __call__(self, data: Iterable[T], chunk_size: int = 1) -> Generator[R, None, None]:
        """
        Applies functor on each element in iterable.
        honors the order

        :param data: iterable of data that should be passed to functor
        :param chunk_size: size of a chunk that is send to a process
        :return: generator of results
        """

        buffer = Buffer()

        def chunking(d):
            ch = []
            for x in d:
                ch.append(x)
                if len(ch) == chunk_size:
                    yield ch
                    ch = []
            if len(ch) > 0:
                yield ch

        data_cnt = 0
        finished_cnt = 0
        for i, chunk in enumerate(chunking(data)):
            self._work_queue.put((i, chunk))
            data_cnt += 1

            try:
                # read the results
                while True:
                    res_i, res_chunk = self._results_queue.get(False)
                    for ch in buffer(res_i, res_chunk):
                        finished_cnt += 1
                        for x in ch:
                            yield x

            except queue.Empty:
                pass

        while finished_cnt < data_cnt:
            res_i, res_chunk = self._results_queue.get()
            for ch in buffer(res_i, res_chunk):
                finished_cnt += 1
                for x in ch:
                    yield x
