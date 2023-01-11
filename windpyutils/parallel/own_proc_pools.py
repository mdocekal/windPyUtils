# -*- coding: UTF-8 -*-
""""
Created on 30.05.22
This module contains multiprocessing pool that allows to use own process classes.

:author:     Martin Dočekal
"""
import math
import multiprocessing
import sys
import threading
from abc import abstractmethod, ABC
from multiprocessing import Process
from multiprocessing.context import BaseContext
from multiprocessing.process import BaseProcess
from threading import Thread
from typing import TypeVar, Iterable, Generator, List, Generic, Optional, Union

from windpyutils.buffers import Buffer

T = TypeVar('T')
R = TypeVar('R')


class BaseFunctorWorker(BaseProcess, Generic[T, R]):
    """
    Functor worker for pools.

    :ivar wid: unique id of this worker
        If None than then the pool will assess one.
    :vartype wid: Any
    :ivar work_queue: queue that is used for receiving work and stop orders
        If None then the default from pool will be used.
    :vartype work_queue: Optional[Queue]
    :ivar results_queue: queue that is used for sending results
        If None then the default from pool will be used.
    :vartype results_queue: Optional[Queue]
    """

    def __init__(self, context: BaseContext, max_chunks_per_worker: float = math.inf):
        """
        Initialization of parallel worker.

        :param context: On which multiprocessing context this pool should operate.
        :param max_chunks_per_worker: Defines maximal number of chunks that a worker will do before it will stop
            New worker will replace it when used with pool that supports replace queue.

            This is particular useful when you observe increasing memory, as it seems there is a known problem
                with that: https://stackoverflow.com/questions/21485319/high-memory-usage-using-python-multiprocessing
        """
        super().__init__()

        self.wid = None
        self.work_queue = None
        self.results_queue = None
        self.replace_queue = None
        self.begin_finished = context.Event()
        self.max_chunks_per_worker = max_chunks_per_worker

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

            while self.max_chunks_per_worker > 0:
                q_item = self.work_queue.get()

                if q_item is None:
                    # all done
                    break

                i, data_list = q_item
                self.results_queue.put((i, [self(x) for x in data_list]))
                self.max_chunks_per_worker -= 1
            else:
                if self.replace_queue is not None:
                    self.replace_queue.put(self.wid)

        finally:
            self.end()


class FunctorWorker(Process, BaseFunctorWorker, ABC):
    """
    Functor worker for pools. Uses default multiprocessing context.

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

    def __init__(self, max_chunks_per_worker: float = math.inf):
        """

        :param max_chunks_per_worker: Defines maximal number of chunks that a worker will do before it will stop
            New worker will replace it when used with pool that supports replace queue.

            This is particular useful when you observe increasing memory, as it seems there is a known problem
                with that: https://stackoverflow.com/questions/21485319/high-memory-usage-using-python-multiprocessing
        """
        Process.__init__(self)
        BaseFunctorWorker.__init__(self, multiprocessing.get_context(), max_chunks_per_worker)


class CMThread(Thread):
    """
    Context manager thread.
    """

    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()
        self.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args, **kwargs):
        self.stop()


class FunctorPool:
    """
    A pool that uses given workers.
    """

    class SendWorkThread(CMThread):
        """
        Thread for sending work to workers.
        """

        def __init__(self, pool: "FunctorPool", data: Iterable[T], chunk_size: int = 1):
            """
            :param pool: pool that is using this thread to send work
            :param data: iterable of data that should be passed to functor
            :param chunk_size: size of a chunk that is sent to a process
            """
            super().__init__()
            self.data = data
            self.chunk_size = chunk_size
            self.pool = pool

        def run(self) -> None:
            self.pool._sending_work = True
            self.pool._data_cnt = 0

            def chunking(d):
                ch = []
                for x in d:
                    ch.append(x)
                    if len(ch) == self.chunk_size:
                        yield ch
                        ch = []
                if len(ch) > 0:
                    yield ch

            for i, chunk in enumerate(chunking(self.data)):
                self.pool._work_queue.put((i, chunk))
                self.pool._data_cnt += 1
                if self.stop_event.is_set():
                    break

            self.pool._sending_work = False

    def __init__(self, workers: List[BaseFunctorWorker[T, R]], context: Optional[BaseContext] = None,
                 work_queue_maxsize: Optional[Union[int, float]] = 1.0,
                 results_queue_maxsize: Optional[Union[int, float]] = None, verbose: bool = False,
                 join_timeout: Optional[int] = None):
        """
        Initialization of pool.

        :param workers: parallel workers.
        :param context: On which multiprocessing context this pool should operate.
        :param work_queue_maxsize: Max size of queue that is used for sending work to workers.
            If None all work will be passed to queue at once.
                float the max size will be: int(workers * work_queue_maxsize)
                int the max size is just work_queue_maxsize
        :param results_queue_maxsize: Max size of queue that is used to deliver results to main process.
            float the max size will be: int(workers * results_queue_maxsize)
            int the max size is just results_queue_maxsize
        :param verbose: Determines whether information messages should be shown.
        :param join_timeout: Timout for process joining.
        """

        if context is None:
            context = multiprocessing.get_context()

        if isinstance(work_queue_maxsize, float):
            work_queue_maxsize = int(len(workers) * work_queue_maxsize)

        if isinstance(results_queue_maxsize, float):
            results_queue_maxsize = int(len(workers) * results_queue_maxsize)

        self._wid_counter = 0
        self._work_queue = context.Queue() if work_queue_maxsize is None else context.Queue(work_queue_maxsize)
        self._results_queue = context.Queue() if results_queue_maxsize is None else context.Queue(results_queue_maxsize)
        self.procs = workers

        self._sending_work = False
        self._data_cnt = 0

        for p in self.procs:
            self._init_process(p)

        self.verbose = verbose
        self.join_timeout = join_timeout

    def _init_process(self, p: BaseFunctorWorker):
        """
        initialization of a process

        :param p: process for initialization
        """

        p.wid = self._wid_counter
        self._wid_counter += 1
        if p.work_queue is None:
            p.work_queue = self._work_queue
        if p.results_queue is None:
            p.results_queue = self._results_queue

    def __enter__(self) -> "FunctorPool":
        for p in self.procs:
            p.start()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        for _ in range(len(self.procs)):
            self._work_queue.put(None)
        for p in self.procs:
            if p.exitcode is None:
                p.join(timeout=self.join_timeout)
                if p.exitcode is None and self.verbose:
                    print(f"Process with wid {p.wid} was not joined and is still running.", file=sys.stderr)

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
        :param chunk_size: size of a chunk that is sent to a process
        :return: generator of results
        """

        buffer = Buffer()
        finished_cnt = 0

        with self.SendWorkThread(self, data, chunk_size):
            while self._sending_work or finished_cnt < self._data_cnt:
                res_i, res_chunk = self._results_queue.get()
                for ch in buffer(res_i, res_chunk):
                    finished_cnt += 1
                    for x in ch:
                        yield x


class FunctorWorkerFactory(ABC):
    """
    Abstract factory for creating new workers
    """

    def create(self) -> BaseFunctorWorker:
        """
        Creates a worker.

        :return: new worker
        """
        ...


class FactoryFunctorPool(FunctorPool):
    """
    A pool that creates workers using provided factory.
    """

    class ReplaceWorkerThread(CMThread):
        """
        Thread for replacing workers.
        """

        def __init__(self, pool: "FactoryFunctorPool", verbose: bool = False):
            """
            :param pool: pool that is using this thread to send work
            :param verbose: Determines whether information messages should be shown.
            """
            super().__init__()
            self.pool = pool
            self.verbose = verbose

        def run(self) -> None:
            while not self.stop_event.is_set():
                replace_id = self.pool._replace_queue.get()
                if replace_id is None:
                    break
                for i, p in enumerate(self.pool.procs):
                    if p.wid == replace_id:
                        replace_index = i
                        p.join(timeout=self.pool.join_timeout)
                        if p.exitcode is None and self.verbose:
                            print(f"Process with wid {p.wid} was not joined and is still running.", file=sys.stderr)
                        break
                else:
                    raise RuntimeError(f"Unknown world id {replace_id}. I am not able to replace this process.")

                p = self.pool._workers_factory.create()
                self.pool._init_process(p)
                self.pool.procs[replace_index] = p
                self.pool.procs[replace_index].start()

        def stop(self):
            self.pool._replace_queue.put(None)
            super().stop()

    def __init__(self, workers: int, workers_factory: FunctorWorkerFactory, context: Optional[BaseContext] = None,
                 work_queue_maxsize: Optional[Union[int, float]] = 1.0,
                 results_queue_maxsize: Optional[Union[int, float]] = None, verbose: bool = False,
                 join_timeout: Optional[int] = None):
        """
        Initialization of pool.

        :param workers: initial number of workers
        :param workers_factory: factory that will be used for creating workers
            It will also use it to create a new worker when a worker stops due to exceeding maximal number of chunks
        :param context: On which multiprocessing context this pool should operate.
        :param work_queue_maxsize: Max size of queue that is used for sending work to workers.
            If None all work will be passed to queue at once.
            If not None it will try to fill up the queue and when it is full it will read the results in the meantime.
                float the max size will be: int(workers * work_queue_maxsize)
                int the max size is just work_queue_maxsize
        :param results_queue_maxsize: Max size of queue that is used to deliver results to main process.
            float the max size will be: int(workers * results_queue_maxsize)
            int the max size is just results_queue_maxsize

            Due to memory usage it might be good idea to put limit on results as it might happen that the work queue
            will never be full which causes that all the results will be read at the end.
        :param verbose: Determines whether information messages should be shown.
        :param join_timeout: Timout for process joining.
        :raise ValueError: when attributes are invalid
        """
        if context is None:
            context = multiprocessing.get_context()

        workers = [workers_factory.create() for _ in range(workers)]

        self._workers_factory = workers_factory
        self._replace_queue = context.Queue()

        super().__init__(workers, context, work_queue_maxsize, results_queue_maxsize, verbose, join_timeout)

    def _init_process(self, p: BaseFunctorWorker):
        super()._init_process(p)
        p.replace_queue = self._replace_queue

    def imap(self, data: Iterable[T], chunk_size: int = 1) -> Generator[R, None, None]:
        """
        Applies functors on each element in iterable.
        honors the order

        :param data: iterable of data that should be passed to functor
        :param chunk_size: size of a chunk that is sent to a process
        :return: generator of results
        """

        with self.ReplaceWorkerThread(self, self.verbose):
            yield from super().imap(data, chunk_size)
