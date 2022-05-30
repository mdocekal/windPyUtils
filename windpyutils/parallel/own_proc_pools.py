# -*- coding: UTF-8 -*-
""""
Created on 30.05.22
This module contains multiprocessing pool that allows to use own process classes.

:author:     Martin Dočekal
"""
import queue
from abc import abstractmethod, ABC
from multiprocessing import Process, Queue, Value, Event
from typing import TypeVar, Iterable, Generator, List, Generic

from windpyutils.buffers import Buffer

T = TypeVar('T')
R = TypeVar('R')


class FunctorWorker(Process, ABC, Generic[T, R]):
    """
    Functor worker for pools.

    :ivar wid: unique id of this worker
        If None than then the pool will asses one.
    :vartype wid: Any
    :ivar work_queue: queue that is used for receiving work and stop orders
        If None then the default from pool will be used.
    :vartype work_queue: Optional[Queue]
    :ivar results_queue: queue that is used for sending results
        If None then the default from pool will be used.
    :vartype results_queue: Optional[Queue]
    """

    def __init__(self):
        """
        Initialization of parallel worker.
        """
        super().__init__()
        self.wid = None
        self.work_queue = None
        self.results_queue = None
        self.begin_finished = Event()

    @abstractmethod
    def __call__(self, inp: T) -> R:
        """
        This method implements the working logic.

        :param inp: data for processing
        :return: processed input
        """
        pass

    def begin(self):
        """
        This method is called as first, before the processing starts, from newly created process.
        """
        pass

    def end(self):
        """
        This method is called at the very end of a process run.
        """
        pass

    def run(self) -> None:
        """
        Run the process.
        """
        try:
            self.begin_finished.clear()
            self.begin()
            self.begin_finished.set()
            while True:
                q_item = self.work_queue.get()

                if q_item is None:
                    # all done
                    break

                i, data_list = q_item

                self.results_queue.put((i, [self(x) for x in data_list]))

        finally:
            self.work_queue.close()
            self.results_queue.close()
            self.end()


class FunctorPool:
    """
    A pool that uses given workers.
    """

    def __init__(self, workers: List[FunctorWorker[T, R]]):
        """
        Initialization of pool.

        :param workers: parallel workers.
        """

        self._work_queue = Queue(len(workers))
        self._results_queue = Queue()
        self.procs = workers

        for i, p in enumerate(self.procs):
            if p.wid is None:
                p.wid = i

            if p.work_queue is None:
                p.work_queue = self._work_queue

            if p.results_queue is None:
                p.results_queue = self._results_queue

    def __enter__(self) -> "FunctorPool":
        for p in self.procs:
            p.daemon = True
            p.start()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        for _ in range(len(self.procs)):
            self._work_queue.put(None)
        for p in self.procs:
            p.join()

    def until_all_ready(self):
        """
        Waits until all process are ready for receiving data.
        It basically waits until all process returns from their begin method.
        """
        for p in self.procs:
            p.begin_finished.wait()

    def imap(self, data: Iterable[T], chunk_size: int = 1) -> Generator[R, None, None]:
        """
        Applies functors on each element in iterable.
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
