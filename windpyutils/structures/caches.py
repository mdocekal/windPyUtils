# -*- coding: UTF-8 -*-
"""
Created on 28.04.23

Module with structures useful for caching.

:author:     Martin Dočekal
"""
from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Iterator, MutableMapping, Dict, TypeVar, Generic

from windpyutils.structures.lists import DoublyLinkedList, DoublyLinkedListNode

_KT = TypeVar("_KT", bound="Comparable")
_VT = TypeVar("_VT")
_MT = TypeVar("_MT")


@dataclass
class Item(Generic[_KT, _VT, _MT]):
    __slots__ = ("key", "value", "meta")
    key: _KT  # key of an item in cache
    value: _VT  # value of an item in cache
    meta: _MT  # meta data


class Cache(MutableMapping[_KT, _VT], ABC):
    """
    Base class for caches.
    """

    def __init__(self, max_size: int):
        """
        Creates new LRU cache.

        :param max_size: Maximum size of the cache.
        """
        self.max_size = max_size

    @abstractmethod
    def __getitem__(self, k: _KT) -> _VT:
        """
        Gets item from cache.

        :param k: Key of the item.
        :return: Value of the item.
        :raise KeyError: When item is not in cache.
        """
        ...

    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[_KT]:
        """
        Iterates over keys of the cache.
        """
        ...

    @abstractmethod
    def __setitem__(self, k: _KT, v: _VT):
        """
        Sets item to the cache.

        :param k: Key of the item.
        :param v: Value of the item.
        """
        ...

    @abstractmethod
    def __delitem__(self, v: _KT) -> None:
        """
        Removes item from cache.

        :param v: Key of the item.
        :raise KeyError: When item is not in cache.
        """
        ...


class LRUCache(Cache):
    """
    Simple LRU cache.
    """

    def __init__(self, max_size: int):
        """
        Creates new LRU cache.

        :param max_size: Maximum size of the cache.
        """
        super().__init__(max_size)
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


class LFUCache(Cache[_KT, _VT]):
    """
    Least frequently used cache.
    """

    def __init__(self, max_size: int):
        """
        Creates new LFU cache.

        :param max_size: Maximum size of the cache.
        """
        super().__init__(max_size)
        self.cache: Dict[_KT, DoublyLinkedListNode[Item[_KT, _VT, int]]] = {}
        self.list: DoublyLinkedList[Item[_KT,_VT, int]] = DoublyLinkedList()

    def __getitem__(self, k: _KT) -> _VT:
        """
        Gets item from cache and increases its frequency.

        :param k: Key of the item.
        :return: Value of the item.
        :raise KeyError: When item is not in cache.
        """
        node = self.cache[k]
        self._inc_freq(node)
        return node.data.value

    def __len__(self) -> int:
        return len(self.cache)

    def __iter__(self) -> Iterator[_KT]:
        """
        Iterates over keys of the cache. From the least frequently used to the most frequently used.

        """
        return (d.key for d in self.list)

    def __setitem__(self, k: _KT, v: _VT):
        """
        Sets item to the cache. If the cache is full the least frequently used item is removed.

        If the item is already in the cache its frequency is increased.

        :param k: Key of the item.
        :param v: Value of the item.
        """

        if k in self.cache:
            node = self.cache[k]
            self._inc_freq(node)
        else:
            if len(self.cache) >= self.max_size:
                # reuse the first node
                node = self.list.head
                del self.cache[node.data.key]
                node.data.key = k
                node.data.value = v
                node.data.meta = 1
            else:
                node = self.list.prepend(Item(k, v, 1))
            self.cache[k] = node

    def __delitem__(self, k: _KT) -> None:
        """
        Removes item from cache.

        :param k: Key of the item.
        :raise KeyError: When item is not in cache.
        """
        node = self.cache[k]
        del self.cache[k]
        self.list.remove(node)

    def _inc_freq(self, node: DoublyLinkedListNode[Item[_KT, _VT, int]], by: int = 1):
        """
        Increases frequency of the node and moves it to the correct place in the list.

        :param node: Node to be increased.
        :param by: By how much.
        """

        node.data.meta += by

        swap_with = node
        while swap_with.next_node is not None and swap_with.next_node.data.meta < node.data.meta:
            swap_with = swap_with.next_node

        if swap_with is not node:
            self.list.move_after(node, swap_with)
