# -*- coding: UTF-8 -*-
""""
Created on 08.04.20
Immutable set for spans.

:author:     Martin Dočekal
"""
import copy
import itertools
from abc import ABC, abstractmethod

from typing import Any, Set, Iterable, Tuple, Iterator, Union, Sequence


class SpanSetEqRelation(ABC):
    """
    Abstract class for equality relation that is used in __contains__ method of SpanSet, to determine if span is
    in given set.
    """

    @abstractmethod
    def __call__(self, xStart: Any, xEnd: Any, yStart: Any, yEnd: Any) -> bool:
        """
        Determines if span x and span y are equal.
        Span x is span on the left side of the in operator and span y is span from investigated set.

        :param xStart: Start of span x.
        :type xStart: Any
        :param xEnd: End of span x.
        :type xEnd: Any
        :param yStart: Start of span y.
        :type yStart: Any
        :param yEnd: End of span y.
        :type yEnd: Any
        :return: Returns bool that determines whether x and y spans are equal (true means equal).
        :rtype: bool
        """
        pass


class SpanSetExactEqRelation(SpanSetEqRelation):
    """
    Span equality relation that considers two spans equal only when they are exactly the same.
    """

    def __call__(self, xStart: float, xEnd: float, yStart: float, yEnd: float) -> bool:
        return xStart == yStart and xEnd == yEnd


class SpanSetPartOfEqRelation(SpanSetEqRelation):
    """
    Span equality relation that considers two spans equal only when x span is part of y span (x is completely inside y).
    """

    def __call__(self, xStart: float, xEnd: float, yStart: float, yEnd: float) -> bool:
        return yStart <= xStart and xEnd <= yEnd


class SpanSetIncludesEqRelation(SpanSetEqRelation):
    """
    Span equality relation that considers two spans equal only when x span includes whole y span.
    """

    def __call__(self, xStart: float, xEnd: float, yStart: float, yEnd: float) -> bool:
        return xStart <= yStart and yEnd <= xEnd


class SpanSetOverlapsEqRelation(SpanSetEqRelation):
    """
    Span equality relation that considers two spans equal only when x span y span shares non empty interval
    (x and y overlaps).

    """

    def __call__(self, xStart: float, xEnd: float, yStart: float, yEnd: float) -> bool:
        # Explanation of condition:
        #   It is easier to start with contradiction, because original relation has much more cases, so...
        #   This relation returns false when there is no overlap:
        #       xs ----------- xe
        #                              ys ----------- ye
        #       xe < ys
        #      or:
        #                              xs ----------- xe
        #        ys ----------- ye
        #       ye < xs
        #
        #   But we are interested in negation, so:
        #   not(xe < ys or ye < xs) =
        #       (xe >= ys) and (ye >= xs)
        return xEnd >= yStart and yEnd >= xStart


class SpanSet(Set):
    """
    Immutable set for spans.

    Implementation comment to standard set operators:
        Unfortunately standard implementation does not handle the eqRelation and seems to return results for regular
        equality (exact match in terms of SpanSetEqRelation). I think it's probably because it uses __eq__ on elements
        itself and so it does not strictly implements the definitions of this operations, for overloaded ∈. Let me
        explain it on the example.
        Union of two sets A and B A ∪ B is defined as:
            A ∪ B = { x∣ x∈A ∨ x∈B }        (where ∈ are custom operators for set A respective B)
        so there is a problem when ∈ (in operator in python notation that is using __contains__ method) has different
        then ordinary behaviour and as I already said it seems the default implementation does not use the operator on
        set level and probably uses __eq__ method on element level, but this is just my guess that led me to own
        implementation.

    :ivar starts: Spans starts.
    :vartype starts: Sequence
    :ivar ends: Spans ends.
    :vartype ends: Sequence
    :ivar eqRelation: New equal relation that determines equality that is used in __contains__ method
        (and at initialization for similar reason)to determine if span is in given set or more precisely
        that span has a span in this set that is equal to it according to that given relation.
    :vartype eqRelation: SpanSetEqRelation
    """

    def __init__(self, starts: Union[Sequence, Iterable[Tuple[Any, Any]]], ends: Sequence = None,
                 forceNoDupCheck: bool = False, eqRelation: SpanSetEqRelation = SpanSetExactEqRelation()):
        """
        Set initialization from iterable of spans or two Sequences. Both Sequence must have the same size,
        because span is composed from offsets on index x in way that span's start is starts[x] and span's end is
        ends[x].

        WARNING: Input Sequences may or not may be reused (not cloned). For more information see forceNoDupCheck param
        documentation.

        :param starts: Spans starts.
            Or iterable of tuples that will be used for initializations and ends will be omitted.
        :type starts: Union[Sequence, Iterable[Tuple[Any, Any]]]
        :param ends: Spans ends.
        :type ends: Sequence
        :param forceNoDupCheck: If true than forces to not use duplicate check of spans in inputs and reuses
            input Sequences, which means that if you now that there are no duplicates, than you will get more memory
            efficient set and also the initialization process will be faster.

            This parameter is not obeyed when starts contains Iterable of spans.
        :type forceNoDupCheck: bool
        :param eqRelation: New equal relation that determines equality that is used in __contains__ method
        (and at initialization for similar reason)to determine if span is in given set or more precisely
        that span has a span in this set that is equal to it according to that given relation.
        :type eqRelation: SpanSetEqRelation
        """

        super().__init__()
        self.eqRelation = eqRelation

        if ends is not None:
            assert len(starts) == len(ends)
            if forceNoDupCheck:
                self.starts = starts
                self.ends = ends
            else:
                # ok we need to look for duplicates
                self.starts = []
                self.ends = []

                for i, s in enumerate(starts):
                    # check if actual span is already in and if not save it to our sequence
                    notIn = True
                    for investigatedSpanIndex in range(len(self.starts)):
                        if self.eqRelation(s, ends[i], self.starts[investigatedSpanIndex],
                                           self.ends[investigatedSpanIndex]):
                            notIn = False
                            break

                    if notIn:
                        self.starts.append(s)
                        self.ends.append(ends[i])

        else:
            self.starts = []
            self.ends = []

            for s, e in starts:
                notIn = True
                for checkIn in range(len(self.starts)):
                    if self.eqRelation(s, e, self.starts[checkIn], self.ends[checkIn]):
                        notIn = False
                        break
                if notIn:
                    self.starts.append(s)
                    self.ends.append(e)

    def __len__(self) -> int:
        return len(self.starts)

    def __str__(self):
        return "{" + ", ".join("({}, {})".format(s, e) for s, e in self) + "}"

    def __iter__(self) -> Iterator[Tuple[Any, Any]]:
        for s, e in zip(self.starts, self.ends):
            yield s, e

    def __contains__(self, span: Tuple[Any, Any]) -> bool:
        for i, s in enumerate(self.starts):
            if self.eqRelation(span[0], span[1], s, self.ends[i]):
                # span that is equal to this one is in this set
                return True
        return False

    def __le__(self, other: 'SpanSet') -> bool:
        """
        Check if actual set is subset of the other set.

        Definition:
           A ⊆ B <=> ∀x (x∈A => x∈B)

        :param other: The other set.
        :type other: 'SpanSet'
        :return: True when this set is subset of the other set.
        :rtype: bool
        """
        return all(x in other for x in self)

    def __lt__(self, other: 'SpanSet') -> bool:
        """
        Check if actual set is proper subset of the other set.

        Definition:
           A ⊂ B <=> ∀x (x∈A => x∈B) ∧ A  ≠ B

        :param other: The other set.
        :type other: 'SpanSet'
        :return: True when this set is proper subset of the other set.
        :rtype: bool
        """
        return self <= other and self != other

    def __eq__(self, other: 'SpanSet') -> bool:
        """
        Check if actual set is equal with other set.

        Definition:
           A = B <=> A ⊆ B ∧ B ⊆ A

        :param other: The other set.
        :type other: 'SpanSet'
        :return: True when this set equal with the other set.
        :rtype: bool
        """
        return self <= other <= self

    def __ne__(self, other: 'SpanSet') -> bool:
        """
        Check if actual set is not equal with the other set.

        :param other: The other set.
        :type other: 'SpanSet'
        :return: True when this set is not equal with the other set.
        :rtype: bool
        """
        return not (self == other)

    def __ge__(self, other: 'SpanSet') -> bool:
        """
        Check if actual set is super set of the other set.

        :param other: The other set.
        :type other: 'SpanSet'
        :return: True when this set is supper set of the other set.
        :rtype: bool
        """
        return other <= self

    def __gt__(self, other: 'SpanSet') -> bool:
        """
        Check if actual set is proper super set of the other set.

        :param other: The other set.
        :type other: 'SpanSet'
        :return: True when this set is proper supper set of the other set.
        :rtype: bool
        """
        return other < self

    def __and__(self, other: 'SpanSet') -> 'SpanSet':
        """
        Returns sets intersection with respect to custom ∈ (in) operator of the set.

        So the definition is:
            A ∩ B = { x ∣ x∈A ∧ x∈B }   (where ∈ are custom operators for set A respective B)

        Note that the result is common set, which means that it uses exact match relation SpanSetExactEqRelation.

        :param other: The other set.
        :type other: 'SpanSet'
        :return: Intersection of both sets.
        :rtype: 'SpanSet'
        """

        return type(self)(x for x in itertools.chain(self, other) if x in self and x in other)

    def __or__(self, other: 'SpanSet') -> 'SpanSet':
        """
        Returns sets union with respect to custom ∈ (in) operator of the set.

        So the definition is:
            A ∪ B = { x ∣ x∈A ∨ x∈B }   (where ∈ are custom operators for set A respective B)

        Note that the result is common set, which means that it uses exact match relation SpanSetExactEqRelation.

        :param other:The other set.
        :type other: 'SpanSet'
        :return: Union of both sets.
        :rtype: 'SpanSet'
        """
        return type(self)(x for x in itertools.chain(self, other) if x in self or x in other)

    def __sub__(self, other) -> 'SpanSet':
        """
        Returns difference of two sets with respect to custom ∈ (in) operator of the set.

        So the definition is:
            A - B = { x ∣ x∈A ∧ x∉B }   (where ∈, ∉ are custom operators for set A respective B)

        Note that the result is common set, which means that it uses exact match relation SpanSetExactEqRelation.

        :param other:The other set.
        :type other: 'SpanSet'
        :return: Difference A - B.
        :rtype: 'SpanSet'
        """

        return type(self)(x for x in itertools.chain(self, other) if x in self and x not in other)

    def __xor__(self, other) -> 'SpanSet':
        """
        Returns symmetric difference of two sets with respect to custom ∈ (in) operator of the set.

        So the definition is:
            A ⊕ B = (A-B) ∪ (B-A) = { x| x∈A xor x∈B }(where ∈, ∉ are custom operators for set A respective B)

        Note that the result is common set, which means that it uses exact match relation SpanSetExactEqRelation.

        :param other:The other set.
        :type other: 'SpanSet'
        :return: Symmetric difference: A ⊕ B.
        :rtype: 'SpanSet'
        """

        return type(self)(x for x in itertools.chain(self, other) if (x in self) ^ (x in other))

    def isdisjoint(self, s: Iterable[Any]) -> bool:
        """
        Checks if iterable is disjoint with actual set.

        :param s: Iterable to check.
        :type s: Iterable[Any]
        :return: Returns true when all elements in iterable are not in this set.
        :rtype: bool
        """

        return all(x not in self for x in s)

    def issubset(self, other: 'SpanSet') -> bool:
        """
        Checks ifs actual set is subset of the other set.

        :param other: Set for check.
        :type other: SpanSet
        :return: True is subset. False otherwise.
        :rtype: bool
        """
        return self <= other

    def issuperset(self, other: 'SpanSet') -> bool:
        """
        Checks ifs actual set is superset of the other set.

        :param other: Set for check.
        :type other: SpanSet
        :return: True is superset. False otherwise.
        :rtype: bool
        """
        return self >= other

    def copy(self) -> 'SpanSet':
        """
        Returns shallow copy of this set.

        :return: Shallow copy.
        :rtype: 'SpanSet'
        """

        return copy.copy(self)
