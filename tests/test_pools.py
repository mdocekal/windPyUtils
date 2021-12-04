# -*- coding: UTF-8 -*-
""""
Created on 04.12.21

:author:     Martin Dočekal
"""
import os
import unittest

from windpyutils.parallel.pools import FunctorMap


class TestFunctorMap(unittest.TestCase):
    def test_map(self):
        if os.cpu_count() > 1:
            workers = 2
            data = [i for i in range(10000)]
            with FunctorMap(lambda x: x * 2, workers=workers) as fm:
                results = list(fm(data))
                self.assertListEqual(results, [i * 2 for i in data])
        else:
            self.skipTest("This test can only be run on the multi cpu device.")

    def test_map_chunk_size(self):
        if os.cpu_count() > 1:
            workers = 2
            data = [i for i in range(10000)]
            with FunctorMap(lambda x: x * 2, workers=workers) as fm:
                results = list(fm(data, chunk_size=250))
                self.assertListEqual(results, [i * 2 for i in data])

            with FunctorMap(lambda x: x * 2, workers=workers) as fm:
                results = list(fm(data, chunk_size=700))
                self.assertListEqual(results, [i * 2 for i in data])
        else:
            self.skipTest("This test can only be run on the multi cpu device.")

    def test_map_all_cpus(self):
        if os.cpu_count() > 1:
            data = [i for i in range(10000)]
            with FunctorMap(lambda x: x * 2, workers=-1) as fm:
                results = list(fm(data))
                self.assertListEqual(results, [i * 2 for i in data])
        else:
            self.skipTest("This test can only be run on the multi cpu device.")


if __name__ == '__main__':
    unittest.main()
