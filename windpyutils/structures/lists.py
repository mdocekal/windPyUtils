# -*- coding: UTF-8 -*-
"""
Created on 28.04.23

:author:     Martin Dočekal
"""
import dataclasses
from typing import Optional, Generic, TypeVar, Generator, Iterable

_T = TypeVar("_T")


@dataclasses.dataclass
class DoublyLinkedListNode(Generic[_T]):
    """
    Single element in doubly linked list.
    """
    data: _T # data of the node
    prev_node: Optional["DoublyLinkedListNode"] = None # link to the previous node
    next_node: Optional["DoublyLinkedListNode"] = None # link to the next node


class DoublyLinkedList(Iterable[_T]):
    """
    Doubly linked list.
    """

    def __init__(self, data: Iterable[_T] = None):
        """
        Creates new doubly linked list.
        """
        self.head = None
        self.tail = None
        self.size = 0

        if data is not None:
            self.extend(data)

    def append(self, data: _T) -> DoublyLinkedListNode[_T]:
        """
        Appends new element to the end of the list.

        Example:
            >>> l = DoublyLinkedList()
            >>> l.append(1)
            >>> l.append(2)
            >>> list(l)
            [1, 2]

        :param data: Data of the new element.
        :return: New node that wraps given data.
        """
        new_node = DoublyLinkedListNode(data, self.tail, None)

        if self.tail is not None:
            self.tail.next_node = new_node
        else:
            self.head = new_node

        self.tail = new_node
        self.size += 1

        return new_node

    def prepend(self, data: _T) -> DoublyLinkedListNode[_T]:
        """
        Prepends new element to the beginning of the list.

        Example:
            >>> l = DoublyLinkedList()
            >>> l.prepend(1)
            >>> l.prepend(2)
            >>> list(l)
            [2, 1]

        :param data: Data of the new element.
        :return: New node that wraps given data.
        """
        new_node = DoublyLinkedListNode(data, None, self.head)

        if self.head is not None:
            self.head.prev_node = new_node
        else:
            self.tail = new_node

        self.head = new_node
        self.size += 1

        return new_node

    def extend(self, data: Iterable[_T]):
        """
        Extends list with given data.

        Example:
            >>> l = DoublyLinkedList([1,2,3])
            >>> l.extend([4,5,6])
            >>> list(l)
            [1, 2, 3, 4, 5, 6]

        :param data: Data to be appended.
        """
        for d in data:
            self.append(d)

    def pre_extend(self, data: Iterable[_T]):
        """
        Extends list with given data, but all elements are prepended.

        Example:
            >>> l = DoublyLinkedList([1,2,3])
            >>> l.pre_extend([4,5,6])
            >>> list(l)
            [6, 5, 4, 1, 2, 3]

        :param data: Data to be prepended.
        """
        for d in data:
            self.prepend(d)

    def remove(self, node: DoublyLinkedListNode[_T]):
        """
        Removes given node from the list.

        Example:
            >>> l = DoublyLinkedList([1,2,3])
            >>> l.remove(l.head.next_node)
            >>> list(l)
            [1, 3]

        :param node: Node to be removed.
        """
        if node.prev_node is not None:
            node.prev_node.next_node = node.next_node
        else:
            self.head = node.next_node

        if node.next_node is not None:
            node.next_node.prev_node = node.prev_node
        else:
            self.tail = node.prev_node

        self.size -= 1

    def pop_back(self) -> _T:
        """
        Removes and returns last element in the list.

        Example:
            >>> l = DoublyLinkedList([1,2,3])
            >>> l.pop()
            3
            >>> list(l)
            [1, 2]

        :return: Last element in the list.
        :raises IndexError: If list is empty.
        """
        if self.tail is None:
            raise IndexError("pop from empty list")

        ret = self.tail.data
        self.remove(self.tail)
        return ret

    def pop_front(self) -> _T:
        """
        Removes and returns first element in the list.

        Example:
            >>> l = DoublyLinkedList([1,2,3])
            >>> l.pop_front()
            1
            >>> list(l)
            [2, 3]

        :return: First element in the list.
        :raises IndexError: If list is empty.
        """
        if self.head is None:
            raise IndexError("pop from empty list")

        ret = self.head.data
        self.remove(self.head)
        return ret

    def __len__(self):
        return self.size

    def iter_nodes(self) -> Generator[DoublyLinkedListNode[_T], None, None]:
        """
        Iterates over all nodes in the list.

        :return: Iterator over all nodes in the list.
        """
        node = self.head
        while node is not None:
            yield node
            node = node.next_node

    def __iter__(self) -> _T:
        """
        Iterates over all data in the list.

        :return: Iterator over all data in the list.
        """
        for node in self.iter_nodes():
            yield node.data

    def move_to_front(self, node: DoublyLinkedListNode[_T]):
        """
        Moves given node to the beginning of the list.

        Example:
            >>> l = DoublyLinkedList([1,2,3])
            >>> l.move_to_front(l.head.next_node)
            >>> list(l)
            [2, 1, 3]

        :param node: Node to be moved.
        :raises RuntimeError: If list is empty.
        """

        if self.head is None:
            raise RuntimeError("Move is not possible on empty list")

        if node.prev_node is None:
            return

        self.remove(node)
        self.head.prev_node = node

        node.prev_node = None
        node.next_node = self.head

        self.head = node

    def move_to_back(self, node: DoublyLinkedListNode[_T]):
        """
        Moves given node to the end of the list.

        Example:
            >>> l = DoublyLinkedList([1,2,3])
            >>> l.move_to_back(l.head)
            >>> list(l)
            [2, 3, 1]

        :param node: Node to be moved.
        :raises RuntimeError: If list is empty.
        """
        if self.head is None:
            raise RuntimeError("Move is not possible on empty list")

        if node.next_node is None:
            return

        self.remove(node)
        self.tail.next_node = node

        node.next_node = None
        node.prev_node = self.tail

        self.tail = node

    def rotate(self, front_to_back: bool = True):
        """
        Rotates the list.

        Example:
            >>> l = DoublyLinkedList([1,2,3,4,5])
            >>> l.rotate()
            >>> list(l)
            [2, 3, 4, 5, 1]

            >>> l = DoublyLinkedList([1,2,3,4,5])
            >>> l.rotate(front_to_back=False)
            >>> list(l)
            [5, 1, 2, 3, 4]

        :param front_to_back: If true first element will be moved to the end of the list.
            False will move last element to the beginning of the list.
        """

        if self.head is None or self.head == self.tail:
            return

        if front_to_back:
            self.tail.next_node = self.head
            self.head.prev_node = self.tail
            self.head = self.head.next_node
            self.head.prev_node = None
            self.tail = self.tail.next_node
            self.tail.next_node = None
        else:
            self.head.prev_node = self.tail
            self.tail.next_node = self.head
            self.tail = self.tail.prev_node
            self.tail.next_node = None
            self.head = self.head.prev_node
            self.head.prev_node = None

    def move_after(self, node: DoublyLinkedListNode[_T], after: DoublyLinkedListNode[_T]):
        """
        Moves a node after another node.

        :param node: node to be inserted
        :param after: node after this node will be inserted
        """

        if node == after:
            return

        self.remove(node)

        if after.next_node is None:
            self.tail = node
        else:
            after.next_node.prev_node = node

        node.next_node = after.next_node
        node.prev_node = after
        after.next_node = node
