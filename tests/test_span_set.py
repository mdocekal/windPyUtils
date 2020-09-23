# -*- coding: UTF-8 -*-
""""
Created on 09.04.20

:author:     Martin Dočekal
"""
import unittest
from collections import Sequence

from windpyutils.structures.span_set import SpanSet, SpanSetExactEqRelation, \
    SpanSetPartOfEqRelation, SpanSetIncludesEqRelation, SpanSetOverlapsEqRelation


class TestSpanSetEqRelation(unittest.TestCase):
    """
    Unit test of span set equality relations.
    """

    def test_exact(self):
        """
        Tests equality relation that considers two spans equal only when they are exactly the same.
        """
        rel = SpanSetExactEqRelation()

        self.assertTrue(rel(1, 1, 1, 1))
        self.assertTrue(rel(1, 2, 1, 2))

        self.assertFalse(rel(2, 4, 1, 5))

    def test_part_of(self):
        """
        Tests equality relation that considers two spans equal only when x span is part of y span (x is completely inside y).
        """
        rel = SpanSetPartOfEqRelation()

        self.assertTrue(rel(3, 4, 1, 10))
        self.assertTrue(rel(3, 4, 3, 4))
        self.assertTrue(rel(1, 1, 1, 1))

        self.assertFalse(rel(3, 5, 4, 5))
        self.assertFalse(rel(3, 6, 4, 7))
        self.assertFalse(rel(3, 6, 5, 5))

    def test_includes(self):
        """
        Tests equality relation that considers two spans equal only when x span includes whole y span.
        """

        rel = SpanSetIncludesEqRelation()

        self.assertTrue(rel(1, 10, 3, 4))
        self.assertTrue(rel(3, 4, 3, 4))
        self.assertTrue(rel(1, 1, 1, 1))

        self.assertFalse(rel(4, 5, 3, 5))
        self.assertFalse(rel(4, 7, 3, 6))
        self.assertFalse(rel(5, 5, 3, 6))

    def test_shared_part(self):
        """
        Tests equality relation that considers two spans equal only when x span y span shares non empty interval
        (x and y overlaps).
        """

        rel = SpanSetOverlapsEqRelation()

        # exact equal
        #   xs --- xe
        #   ys --- ye
        self.assertTrue(rel(1, 1, 1, 1))
        self.assertTrue(rel(3, 4, 3, 4))

        # xs ----------- xe
        #     ys---ye
        self.assertTrue(rel(1, 10, 3, 4))

        #     xs---xe
        # ys ----------- ye
        self.assertTrue(rel(3, 4, 1, 10))

        # xs ----------- xe
        #       ys ----------- ye
        self.assertTrue(rel(1, 10, 3, 11))

        #       xs ----------- xe
        # ys ----------- ye
        self.assertTrue(rel(4, 10, 1, 5))

        # xs ----------- xe
        #                ys ----------- ye
        self.assertTrue(rel(1, 5, 5, 10))

        #                xs ----------- xe
        # ys ----------- ye
        self.assertTrue(rel(5, 7, 1, 5))

        # xs ----------- xe
        #                       ys ----------- ye
        self.assertFalse(rel(1, 2, 4, 6))

        #                       xs ----------- xe
        # ys ----------- ye
        self.assertFalse(rel(1, 1, 0, 0))
        self.assertFalse(rel(10, 20, 0, 5))


class TestSpanSet(unittest.TestCase):
    """
    Unit test class for SpanSet util.
    """

    def setUp(self) -> None:
        self.starts = [1, 2, 3, 4, 5, 1]
        self.ends = [1, 2, 3, 4, 5, 2]

        self.starts2 = [1, 2, 3, 4, 5, 1]
        self.ends2 = [3, 4, 3, 7, 5, 2]

        self.startsDuplicate = [1, 2, 3, 2, 5, 1]
        self.endsDuplicate = [1, 2, 3, 2, 5, 3]

        self.A = SpanSet([1, 2, 3, 4, 5], [3, 4, 5, 6, 7], forceNoDupCheck=True)
        self.APartOf = self.A.copy()
        self.APartOf.eqRelation = SpanSetPartOfEqRelation()
        self.AIncludes = self.A.copy()
        self.AIncludes.eqRelation = SpanSetIncludesEqRelation()
        self.AOverlaps = self.A.copy()
        self.AOverlaps.eqRelation = SpanSetOverlapsEqRelation()

        self.B = SpanSet([11, 3, 4, 5], [13, 5, 6, 8], forceNoDupCheck=True)
        self.BPartOf = self.B.copy()
        self.BPartOf.eqRelation = SpanSetPartOfEqRelation()
        self.BIncludes = self.B.copy()
        self.BIncludes.eqRelation = SpanSetIncludesEqRelation()
        self.BOverlaps = self.B.copy()
        self.BOverlaps.eqRelation = SpanSetOverlapsEqRelation()

        # A ∪ B
        self.AUB = SpanSet([1, 2, 3, 4, 5, 11, 5], [3, 4, 5, 6, 7, 13, 8],
                           forceNoDupCheck=True)
        # A ∩ B
        self.AIB = SpanSet([3, 4], [5, 6],
                           forceNoDupCheck=True)
        self.AIBPartOf = SpanSet([3, 4, 5], [5, 6, 7],
                                 forceNoDupCheck=True)
        self.AIBOverlaps = SpanSet([1, 2, 3, 4, 5], [3, 4, 5, 6, 7],
                                   forceNoDupCheck=True)

        # A - B
        self.ADifB = SpanSet([1, 2, 5], [3, 4, 7], forceNoDupCheck=True)
        self.ADifBPartOf = SpanSet([1, 2], [3, 4], forceNoDupCheck=True)
        self.ADifBOverlaps = SpanSet([], [], forceNoDupCheck=True)

        # A ⊕ B (symmetric difference)
        self.ADifSymB = SpanSet([1, 2, 5, 11, 5], [3, 4, 7, 13, 8], forceNoDupCheck=True)
        self.ADifSymBPartOf = SpanSet([1, 2, 11, 5], [3, 4, 13, 8], forceNoDupCheck=True)
        self.ADifSymBOverlaps = SpanSet([11, 5], [13, 8], forceNoDupCheck=True)

        # A subset
        self.ASubset = SpanSet([2, 3], [4, 5], forceNoDupCheck=True)
        self.APartOfSubset = SpanSet([2, 3, 6], [4, 5, 6], forceNoDupCheck=True)
        self.AIncludesSubset = SpanSet([2, 3, 4], [4, 5, 8], forceNoDupCheck=True)
        self.AOverlapsSubset = SpanSet([2, 3, 7], [4, 5, 9], forceNoDupCheck=True)

        # A superset
        self.ASup = SpanSet([1, 2, 3, 4, 5, 6], [3, 4, 5, 6, 7, 9], forceNoDupCheck=True)
        self.AOverlapsSup = SpanSet([1, 2, 3, 4, 5, 20], [3, 4, 5, 6, 7, 21],
                                    forceNoDupCheck=True)

        self.AEq = SpanSet([1, 2, 3, 4, 5], [3, 4, 5, 6, 7], forceNoDupCheck=True)
        self.APartOfEq = SpanSet([1, 2, 3, 4, 5, 6], [3, 4, 5, 6, 7, 6],
                                 forceNoDupCheck=True)
        self.AIncludesEq = SpanSet([1, 2, 3, 4, 5, 5], [3, 4, 5, 6, 7, 9],
                                   forceNoDupCheck=True)
        self.AOverlapsEq = SpanSet([1, 2, 3, 4, 5, 7], [3, 4, 5, 6, 7, 10],
                                   forceNoDupCheck=True)

        self.empty = SpanSet([], [], forceNoDupCheck=True)

    def test_non_duplicate_initialization(self):
        """
        Tests set that is initialized with no duplicates.
        """

        sSet = SpanSet(self.starts, self.ends)

        self._checkInit(sSet, self.starts, self.ends)

    def test_non_duplicate_force_no_check_initialization(self):
        """
        Tests set that is initialized with no duplicates and no check is forced.
        """

        sSet = SpanSet(self.starts, self.ends, forceNoDupCheck=True)
        self._checkInit(sSet, self.starts, self.ends)

    def test_duplicate_initialization(self):
        """
        Tests set that is initialized with duplicates.
        """
        sSet = SpanSet(self.startsDuplicate, self.endsDuplicate)

        self._checkInit(sSet, self.startsDuplicate, self.endsDuplicate, duplicates=1)  # there is one duplicate in input

    def test_duplicate_force_no_check_initialization(self):
        """
        Tests set that is initialized with duplicates and no check is forced.
        """
        sSet = SpanSet(self.startsDuplicate, self.endsDuplicate, forceNoDupCheck=True)
        # these set should be wrongly initialized because there are duplicates in the input and we do not perform the
        # check. This test tests that the check was not done (At least, that it has no effect.).

        self.assertEqual(len(sSet), len(self.startsDuplicate))

    def test_eq(self):
        self.assertEqual(self.A, self.AEq)
        self.assertNotEqual(self.A, self.B)

    def test_eq_part_of(self):
        self.assertEqual(self.APartOf, self.AEq)
        self.assertEqual(self.APartOf, self.APartOfEq)
        self.assertNotEqual(self.APartOf, self.B)

    def test_eq_includes(self):
        self.assertEqual(self.AIncludes, self.AEq)
        self.assertEqual(self.AIncludes, self.AIncludesEq)
        self.assertNotEqual(self.AIncludes, self.B)

    def test_eq_overlaps(self):
        self.assertEqual(self.AOverlaps, self.AEq)
        self.assertEqual(self.AOverlaps, self.AOverlapsEq)
        self.assertNotEqual(self.AOverlaps, self.B)

    def test_in(self):
        self.assertTrue((1, 3) in self.A)
        self.assertFalse((100, 300) in self.A)

    def test_in_part_of(self):
        self.assertTrue((1, 3) in self.APartOf)
        self.assertTrue((6, 7) in self.APartOf)
        self.assertTrue((2, 2) in self.APartOf)
        self.assertTrue((5, 6) in self.APartOf)

        self.assertFalse((10, 12) in self.APartOf)
        self.assertFalse((100, 300) in self.APartOf)

    def test_in_includes(self):
        self.assertTrue((1, 3) in self.AIncludes)
        self.assertTrue((4, 7) in self.AIncludes)
        self.assertTrue((2, 4) in self.AIncludes)

        self.assertFalse((10, 12) in self.AIncludes)
        self.assertFalse((100, 300) in self.AIncludes)

    def test_in_overlaps(self):
        self.assertTrue((1, 3) in self.AOverlaps)
        self.assertTrue((6, 7) in self.AOverlaps)
        self.assertTrue((2, 2) in self.AOverlaps)
        self.assertTrue((5, 6) in self.AOverlaps)

        self.assertFalse((10, 12) in self.AOverlaps)
        self.assertFalse((100, 300) in self.AOverlaps)

    def test_subset(self):
        self.assertTrue(self.ASubset.issubset(self.A))
        self.assertFalse(self.B.issubset(self.A))

    def test_subset_part_of(self):
        self.assertTrue(self.ASubset.issubset(self.APartOf))
        self.assertTrue(self.APartOfSubset.issubset(self.APartOf))
        self.assertFalse(self.B.issubset(self.APartOf))

    def test_subset_includes(self):
        self.assertTrue(self.ASubset.issubset(self.AIncludes))
        self.assertTrue(self.AIncludesSubset.issubset(self.AIncludes))
        self.assertFalse(self.B.issubset(self.AIncludes))

    def test_subset_overlaps(self):
        self.assertTrue(self.ASubset.issubset(self.AOverlaps))
        self.assertTrue(self.AOverlapsSubset.issubset(self.AOverlaps))
        self.assertFalse(self.B.issubset(self.AOverlaps))

    def test_superset(self):
        self.assertTrue(self.ASup.issuperset(self.A))
        self.assertFalse(self.B.issuperset(self.A))

    def test_superset_part_of(self):
        self.assertTrue(self.ASup.issuperset(self.APartOf))
        self.assertFalse(self.B.issuperset(self.APartOf))

    def test_superset_includes(self):
        self.assertTrue(self.ASup.issuperset(self.AIncludes))
        self.assertFalse(self.B.issuperset(self.AIncludes))

    def test_superset_overlaps(self):
        self.assertTrue(self.AOverlapsSup.issuperset(self.AOverlaps))
        self.assertFalse(self.B.issuperset(self.AOverlaps))

    def test_union(self):
        self.assertEqual(self.A | self.AEq, self.A)
        self.assertEqual(self.A | self.B, self.AUB)

    def test_union_part_of(self):
        self.assertEqual(self.A | self.APartOfEq, self.APartOfEq)
        self.assertEqual(self.A | self.BPartOf, self.AUB)

    def test_union_includes(self):
        self.assertEqual(self.A | self.AIncludesEq, self.AIncludesEq)
        self.assertEqual(self.A | self.BIncludes, self.AUB)

    def test_union_overlaps(self):
        self.assertEqual(self.A | self.AOverlapsEq, self.AOverlapsEq)
        self.assertEqual(self.A | self.BOverlaps, self.AUB)

    def test_intersection(self):
        self.assertEqual(self.A & self.AEq, self.A)
        self.assertEqual(self.A & self.B, self.AIB)

    def test_intersection_part_of(self):
        self.assertEqual(self.A & self.APartOfEq, self.A)
        self.assertEqual(self.A & self.BPartOf, self.AIBPartOf)

    def test_intersection_includes(self):
        self.assertEqual(self.A & self.AIncludesEq, self.A)
        self.assertEqual(self.A & self.BIncludes, self.AIB)

    def test_intersection_overlaps(self):
        self.assertEqual(self.A & self.AOverlapsEq, self.A)
        self.assertEqual(self.A & self.BOverlaps, self.AIBOverlaps)

    def test_difference(self):
        self.assertEqual(self.A - self.AEq, self.empty)
        self.assertEqual(self.A - self.B, self.ADifB)

    def test_difference_part_of(self):
        self.assertEqual(self.A - self.APartOfEq, self.empty)
        self.assertEqual(self.A - self.BPartOf, self.ADifBPartOf)

    def test_difference_includes(self):
        self.assertEqual(self.A - self.AIncludesEq, self.empty)
        self.assertEqual(self.A - self.BIncludes, self.ADifB)

    def test_difference_overlaps(self):
        self.assertEqual(self.A - self.AOverlapsEq, self.empty)
        self.assertEqual(self.A - self.BOverlaps, self.ADifBOverlaps)

    def test_sym_difference(self):
        self.assertEqual(self.A ^ self.AEq, self.empty)
        self.assertEqual(self.A ^ self.B, self.ADifSymB)

    def test_sym_difference_part_of(self):
        self.assertEqual(self.APartOf ^ self.APartOfEq, self.empty)
        self.assertEqual(self.A ^ self.BPartOf, self.ADifSymBPartOf)

    def test_sym_difference_includes(self):
        self.assertEqual(self.AIncludesEq ^ self.AIncludesEq, self.empty)
        self.assertEqual(self.A ^ self.BIncludes, self.ADifSymB)

    def test_sym_difference_overlaps(self):
        self.assertEqual(self.AOverlapsEq ^ self.AOverlapsEq, self.empty)
        self.assertEqual(self.A ^ self.BOverlaps, self.ADifSymBOverlaps)

    def _checkInit(self, sSet: SpanSet, starts: Sequence, ends: Sequence, duplicates: int = 0):
        """
        Check initialization of SpanSet that was initialized with given tensors.

        :param sSet: Set you want to check.
        :type sSet: SpanSet
        :param starts: Starts used for initialization of the set.
        :type starts: Sequence
        :param ends: Ends used for initialization of the set.
        :type ends: torch.tensor
        :param duplicates: Number of duplicates in input.
            If we have these two tensors:
                [1,2,1]
                [2,3,2]
            Then this parameter should be equal to one, because there are two spans that are the same and therefor
            number of duplicates is one.
        :type duplicates: int
        """

        self.assertEqual(len(sSet), len(starts) - duplicates)

        for span in sSet:
            isIn = False
            for s, e in zip(starts, ends):
                if s == span[0] and e == span[1]:
                    isIn = True
                    break
            self.assertTrue(isIn)

        for s, e in zip(starts, ends):
            self.assertTrue((s, e) in sSet)


if __name__ == '__main__':
    unittest.main()
