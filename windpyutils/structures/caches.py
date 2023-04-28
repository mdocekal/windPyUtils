# -*- coding: UTF-8 -*-
"""
Created on 28.04.23

Module with structures useful for caching.

:author:     Martin Dočekal
"""
from typing import Iterator, MutableMapping, Dict, TypeVar

from windpyutils.structures.lists import DoublyLinkedList, DoublyLinkedListNode

_KT = TypeVar("_KT", bound="Comparable")
_VT = TypeVar("_VT")


class LRUCache(MutableMapping[_KT, _VT]):
    """
    Simple LRU cache.
    """

    def __init__(self, max_size: int):
        """
        Creates new LRU cache.

        :param max_size: Maximum size of the cache.
        """
        self.max_size = max_size
        self.cache: Dict[_KT, DoublyLinkedListNode[_VT]] = {}
        self.list: DoublyLinkedList[_VT] = DoublyLinkedList()

    def __getitem__(self, k: _KT) -> _VT:
        """
        Gets item from cache and moves it to the front in the LRU list.

        :param k: Key of the item.
        :return: Value of the item.
        :raise KeyError: When item is not in cache.
        """
        node = self.cache[k]
        self.list.move_to_front(node)
        return node.data[1]

    def __len__(self) -> int:
        return len(self.cache)

    def __iter__(self) -> Iterator[_KT]:
        """
        Iterates over keys of the cache. From the most recently used to the least recently used.

        """
        return (d[0] for d in self.list)

    def __setitem__(self, k: _KT, v: _VT):
        """
        Sets item to the cache. If the cache is full the least recently used item is removed.

        If the item is already in the cache it is moved to the front in the LRU list and its value is updated.

        :param k: Key of the item.
        :param v: Value of the item.
        """

        if k in self.cache:
            node = self.cache[k]
            node.data = (k, v)
            self.list.move_to_front(node)
        else:
            if len(self.cache) >= self.max_size:
                # reuse the last node
                node = self.list.tail
                del self.cache[node.data[0]]
                node.data = (k, v)
                self.list.move_to_front(node)
            else:
                node = self.list.prepend((k, v))
            self.cache[k] = node

    def __delitem__(self, v: _KT) -> None:
        """
        Removes item from cache.

        :param v: Key of the item.
        :raise KeyError: When item is not in cache.
        """
        node = self.cache[v]
        del self.cache[v]
        self.list.remove(node)
