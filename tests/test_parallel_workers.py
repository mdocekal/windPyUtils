# -*- coding: UTF-8 -*-
""""
Created on 23.09.20

:author:     Martin Dočekal
"""
import os
import queue
import unittest

from windpyutils.parallel.workers import FunRunner


class TestFunRunner(unittest.TestCase):
    def test_run(self):
        if os.cpu_count() > 1:
            workers = os.cpu_count()

            def f(x):
                return x * 2

            data = [x for x in range(1000)]
            procs = [FunRunner(pf=f) for _ in range(workers)]

            for p in procs:
                p.daemon = True
                p.start()

            dataCnt = 0

            res = []

            # push data to workers
            for i, d in enumerate(data):
                FunRunner.WORK_QUEUE.put((i, d))
                dataCnt += 1

                try:
                    # read the results
                    while True:
                        res.append(FunRunner.RESULTS_QUEUE.get(False))
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

            self.assertListEqual([r for i, r in sorted(res, key=lambda x: x[0])], [2*x for x in data])
        else:
            self.skipTest("This test can only be run on the multi cpu device.")


if __name__ == '__main__':
    unittest.main()
