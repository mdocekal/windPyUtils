# -*- coding: UTF-8 -*-
""""
Created on 23.09.20
This module contains classes that represents parallel workers a.k.a. processes.

:author:     Martin Dočekal
"""
import multiprocessing
from multiprocessing.context import Process
from multiprocessing import Queue
from typing import TypeVar, Callable

T = TypeVar('T')
R = TypeVar('R')


class FunRunner(Process):
    """
    Representation of one parallel process that runs given function on data from shared queue :py:attr:`~WORK_QUEUE`
    (shared among all the others FunRunners). It expects that the data is tuple
    (IS_MEANT_FOR_IDS_BUT_CAN_BY_ANYTHING_YOU_WANT, List[data]) or None.
    The None should be put into :py:attr:`~WORK_QUEUE` to terminate a FunRunner.

    The results are put into the :py:attr:`~RESULTS_QUEUE`.

    Example:
        procs = [FunRunner(pf=f) for _ in range(workers)]

        for p in procs:
            p.daemon = True
            p.start()

        dataCnt = 0

        res = []
        # push data to workers
        for i, d in enumerate(data):
            FunRunner.WORK_QUEUE.put((i, [d]))
            dataCnt += 1

            try:
                # read the results
                while True:
                    res.append(FunRunner.RESULTS_QUEUE.get(False)[0])
            except queue.Empty:
                pass

        # terminate running workers
        for _ in range(workers):
            FunRunner.WORK_QUEUE.put(None)

        # get the rest of results
        while len(res) < dataCnt:
            res.append(FunRunner.RESULTS_QUEUE.get())

        for p in procs:
            p.join()
    """

    WORK_QUEUE = Queue(multiprocessing.cpu_count())
    """Queue for work that needs to be done."""

    RESULTS_QUEUE = Queue()
    """Completed work."""

    def __init__(self, pf: Callable[[T], R]):
        """
        Initialization of parallel worker.

        :param pf: Function you want to run in data-parallel way.
        :type pf: Callable[[T], R]
        """
        super().__init__()
        self.pf = pf

    def run(self) -> None:
        """
        Run the process.
        """
        try:
            while True:
                q_item = self.WORK_QUEUE.get()

                if q_item is None:
                    # all done
                    break

                i, data_list = q_item

                self.RESULTS_QUEUE.put((i, [self.pf(x) for x in data_list]))

        finally:
            self.WORK_QUEUE.close()
            self.RESULTS_QUEUE.close()
