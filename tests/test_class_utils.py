# -*- coding: UTF-8 -*-
"""
Created on 30.03.23

:author:     Martin Dočekal
"""
import unittest
from abc import abstractmethod, ABC

from windpyutils.class_utils import sub_cls_from_its_name, subclasses


class A:
    pass


class B(A):
    pass


class C(A):
    pass


class D(B):
    pass


class E(C):
    pass


class F(D):
    pass


class G(E):
    pass


class H(F):
    pass


class BAbc(B, ABC):
    @abstractmethod
    def abc_method(self):
        pass


class BaseOfAnotherConfigurableClass:
    ...


class AnotherConfigurableClass(BaseOfAnotherConfigurableClass):

    def __init__(self, c: str, d: str):
        self.c = c
        self.d = d


class TestSubclasses(unittest.TestCase):
    def test_subclasses(self):
        self.assertEqual(set(subclasses(A)), {B, C, D, E, F, G, H})

    def test_subclasses_abstract(self):
        self.assertEqual(set(subclasses(A, abstract_ok=True)), {B, C, D, E, F, G, H, BAbc})


class TestSubClsFromItsName(unittest.TestCase):

    def test_sub_cls_from_its_name(self):
        self.assertEqual(sub_cls_from_its_name(A, "B"), B)
        self.assertEqual(sub_cls_from_its_name(A, "C"), C)
        self.assertEqual(sub_cls_from_its_name(A, "D"), D)
        self.assertEqual(sub_cls_from_its_name(A, "E"), E)
        self.assertEqual(sub_cls_from_its_name(A, "F"), F)
        self.assertEqual(sub_cls_from_its_name(A, "G"), G)
        self.assertEqual(sub_cls_from_its_name(A, "H"), H)

        with self.assertRaises(ValueError):
            sub_cls_from_its_name(A, "NotExisting")

    def test_sub_cls_from_its_name_abstract(self):
        self.assertEqual(sub_cls_from_its_name(A, "BAbc", abstract_ok=True), BAbc)

        with self.assertRaises(ValueError):
            sub_cls_from_its_name(A, "NotExisting", abstract_ok=True)
