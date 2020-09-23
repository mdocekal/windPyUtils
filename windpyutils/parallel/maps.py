# -*- coding: UTF-8 -*-
""""
Created on 23.09.20
Module with mapping functions.

:author:     Martin Dočekal
"""
import multiprocessing
import queue
from typing import TypeVar, Callable, Iterable, List

from windpyutils.parallel.workers import FunRunner

T = TypeVar('T')
R = TypeVar('R')


def mulPMap(f: Callable[[T], R], data: Iterable[T], workers: int = -1) -> List[R]:
    """
    Runs function f with arguments X

    :param f: Function you want to run in data-parallel way
    :type f: Callable[[T], R]
    :param data: The data that will be processed.
    :type data:Iterable[T]
    :param workers: Number of parallel workers.
        Values <=0 will create number of workers that will be same as number of cpus.
    :type workers: int
    :return: Processed input.
    :rtype:
    """
    if workers <= 0:
        workers = multiprocessing.cpu_count()

    procs = [FunRunner(pf=f) for _ in range(workers)]

    for p in procs:
        p.daemon = True
        p.start()

    dataCnt = 0

    res = []

    for i, d in enumerate(data):
        FunRunner.WORK_QUEUE.put((i, d))
        dataCnt += 1

        try:
            # read the results
            while True:
                res.append(FunRunner.RESULTS_QUEUE.get(False))
        except queue.Empty:
            pass

    for _ in range(workers):
        FunRunner.WORK_QUEUE.put(None)

    while len(res) < dataCnt:
        res.append(FunRunner.RESULTS_QUEUE.get())

    for p in procs:
        p.join()

    return [r for i, r in sorted(res, key=lambda x: x[0])]
