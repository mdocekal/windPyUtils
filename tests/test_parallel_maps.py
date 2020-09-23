# -*- coding: UTF-8 -*-
""""
Created on 23.09.20

:author:     Martin Dočekal
"""
import os
import unittest

from windpyutils.parallel.maps import mulPMap


class TestMulPMap(unittest.TestCase):
    def test_mul_pmap(self):
        if os.cpu_count() > 1:
            workers = 2
            data = [i for i in range(1000)]
            results = mulPMap(lambda x: x*2, data, workers)

            self.assertListEqual(results, [i*2 for i in data])
        else:
            self.skipTest("This test can only be run on the multi cpu device.")

    def test_mul_pmap_all_cpus(self):
        if os.cpu_count() > 1:
            data = [i for i in range(1000)]
            results = mulPMap(lambda x: x * 2, data, -1)

            self.assertListEqual(results, [i * 2 for i in data])
        else:
            self.skipTest("This test can only be run on the multi cpu device.")


if __name__ == '__main__':
    unittest.main()
