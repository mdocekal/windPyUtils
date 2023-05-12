# -*- coding: UTF-8 -*-
"""
Created on 28.04.23

:author:     Martin Dočekal
"""
from unittest import TestCase

from windpyutils.structures.lists import DoublyLinkedList


class TestDoublyLinkedList(TestCase):

    def setUp(self) -> None:
        self.list_empty = DoublyLinkedList()
        self.list = DoublyLinkedList([1, 2, 3, 4, 5])

    def test_len(self):
        self.assertEqual(0, len(self.list_empty))
        self.assertEqual(5, len(self.list))

    def test_append(self):
        self.list_empty.append(10)
        self.list_empty.append(20)
        self.list_empty.append(30)
        self.assertSequenceEqual([10, 20, 30], list(self.list_empty))

        self.list.append(10)
        self.list.append(20)
        self.list.append(30)
        self.assertSequenceEqual([1, 2, 3, 4, 5, 10, 20, 30], list(self.list))

    def test_prepend(self):
        self.list_empty.prepend(10)
        self.list_empty.prepend(20)
        self.list_empty.prepend(30)
        self.assertSequenceEqual([30, 20, 10], list(self.list_empty))

        self.list.prepend(10)
        self.list.prepend(20)
        self.list.prepend(30)
        self.assertSequenceEqual([30, 20, 10, 1, 2, 3, 4, 5], list(self.list))

    def test_extend(self):
        self.list_empty.extend([10, 20, 30])
        self.assertSequenceEqual([10, 20, 30], list(self.list_empty))

        self.list.extend([10, 20, 30])
        self.assertSequenceEqual([1, 2, 3, 4, 5, 10, 20, 30], list(self.list))

    def test_pre_extend(self):
        self.list_empty.pre_extend([10, 20, 30])
        self.assertSequenceEqual([30, 20, 10], list(self.list_empty))

        self.list.pre_extend([10, 20, 30])
        self.assertSequenceEqual([30, 20, 10, 1, 2, 3, 4, 5], list(self.list))

    def test_remove(self):
        self.list.remove(self.list.head.next_node)
        self.assertSequenceEqual([1, 3, 4, 5], list(self.list))

    def test_pop_back(self):
        with self.assertRaises(IndexError):
            self.list_empty.pop_back()
        self.assertEqual(5, self.list.pop_back())
        self.assertSequenceEqual([1, 2, 3, 4], list(self.list))

    def test_pop_front(self):
        with self.assertRaises(IndexError):
            self.list_empty.pop_front()
        self.assertEqual(1, self.list.pop_front())
        self.assertSequenceEqual([2, 3, 4, 5], list(self.list))

    def test_iter_nodes(self):
        self.assertSequenceEqual([1, 2, 3, 4, 5], [n.data for n in self.list.iter_nodes()])
        self.assertSequenceEqual([], [n.data for n in self.list_empty.iter_nodes()])

    def test_move_to_front(self):
        with self.assertRaises(RuntimeError):
            self.list_empty.move_to_front(self.list_empty.head)

        self.list.move_to_front(self.list.head)
        self.assertSequenceEqual([1, 2, 3, 4, 5], list(self.list))
        self.list.move_to_front(self.list.head.next_node)
        self.assertSequenceEqual([2, 1, 3, 4, 5], list(self.list))

    def test_move_to_back(self):
        with self.assertRaises(RuntimeError):
            self.list_empty.move_to_back(self.list_empty.head)

        self.list.move_to_back(self.list.tail)
        self.assertSequenceEqual([1, 2, 3, 4, 5], list(self.list))
        self.list.move_to_back(self.list.head.next_node)
        self.assertSequenceEqual([1, 3, 4, 5, 2], list(self.list))

    def test_rotate(self):
        self.list_empty.rotate()
        self.assertSequenceEqual([], list(self.list_empty))

        self.list.rotate()
        self.assertSequenceEqual([2, 3, 4, 5, 1], list(self.list))

        self.list.rotate(False)
        self.assertSequenceEqual([1, 2, 3, 4, 5], list(self.list))

    def test_move_after(self):
        n = self.list.head
        self.list.move_after(n, n.next_node)
        self.assertSequenceEqual([2, 1, 3, 4, 5], list(self.list))
        self.list.move_after(n, n.next_node)
        self.assertSequenceEqual([2, 3, 1, 4, 5], list(self.list))
        self.list.move_after(n, n.next_node)
        self.assertSequenceEqual([2, 3, 4, 1, 5], list(self.list))
        self.list.move_after(n, n.next_node)
        self.assertSequenceEqual([2, 3, 4, 5, 1], list(self.list))

