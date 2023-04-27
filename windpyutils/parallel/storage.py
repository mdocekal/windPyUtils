# -*- coding: UTF-8 -*-
"""
Created on 27.04.23

This module contains classes that are used to store data in parallel processes.

:author:     Martin Dočekal
"""
import multiprocessing
from abc import abstractmethod
from multiprocessing import Manager
from typing import Generic, TypeVar, Optional, List, Tuple, Generator

T = TypeVar("T")


class Storage(Generic[T]):
    """
    Base class for storage classes.
    """

    @abstractmethod
    def __setitem__(self, global_identifier: int, data: T):
        """
        Stores given data.

        :param global_identifier: identifier that is unique for this data among all processes
        :param data: Data to be stored.
        """
        ...

    @abstractmethod
    def __getitem__(self, global_identifier: int) -> T:
        """
        Returns data stored under given identifier.

        :param global_identifier: identifier that is unique for this data among all processes
        :return: Data stored under given identifier.
        """
        ...

    @abstractmethod
    def __len__(self) -> int:
        """
        Returns number of stored data.

        :return: Number of stored data.
        """
        ...

    @abstractmethod
    def __iter__(self):
        """
        Returns iterator over stored data.

        :return: Iterator over stored data.
        """
        ...


class TextFileStorage(Storage[str]):
    """
    Storage that stores data in files.
    It will create file for each process.
    """

    def __init__(self, path: Optional[str], file_prefix: Optional[str] = "storage",
                 number_of_data: Optional[int] = None, reader_only: bool = False):
        """
        Initialization of file storage.

        :param path: Path to directory where data will be stored.
        :param file_prefix: Prefix of file names.
        :param number_of_data: Number of data that will be stored.
         If you know this number in advance it will be more efficient.
        :param reader_only: If True then this storage will be used only for reading.
            It will not create any files.
        """
        self._path = path
        self._file_prefix = file_prefix
        self._manager = Manager()
        self._file_paths = self._manager.list()
        self._file = None
        self._process_identifier = None

        self._index: List[Optional[Tuple[int, int]]] = self._manager.list()  # (process_identifier, file_offset)
        if number_of_data is not None:
            self._index.extend([None] * number_of_data)

        self._stored_cnt = multiprocessing.Value('i', 0)

        self._storage_lock = multiprocessing.RLock()
        self._file_paths_lock = multiprocessing.RLock()

        self._opened_files_for_reading = []
        self.reader_only = reader_only

        self._waiting_for = multiprocessing.Value('i', 0)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        """
        Opens storage for writing and assigns process identifier.
        """
        if self.reader_only:
            # we are not writing
            return

        if self._file is not None:
            # already opened
            return

        if self._process_identifier is None:
            with self._file_paths_lock:
                self._process_identifier = len(self._file_paths)
                path = self._path + "/" + self._file_prefix + "_" + str(self._process_identifier)
                self._file_paths.append(path)
            self._file = open(path, "w")
        else:
            self._file = open(self._file_paths[self._process_identifier], "a")

    def close(self):
        """
        Closes storage for writing.
        """
        if self._file is not None:
            self._file.close()

        for f in self._opened_files_for_reading:
            if f is not None:
                f.close()

    def is_contiguous(self) -> bool:
        """
        Returns True if there is no gap between stored data.
        All global identifiers are filling the range [0, len(self)) without any gaps.
        """
        return self._waiting_for.value == len(self)

    def _open_file_for_read(self, process_identifier: int):
        """
        Opens file for reading if it is not already opened.

        :param process_identifier: Process identifier.
        """
        if process_identifier >= len(self._opened_files_for_reading):
            self._opened_files_for_reading.extend(
                [None] * (process_identifier - len(self._opened_files_for_reading) + 1)
            )

        if self._opened_files_for_reading[process_identifier] is None:
            self._opened_files_for_reading[process_identifier] = open(self._file_paths[process_identifier], "r")

    def _is_file_open_for_read(self, process_identifier: int) -> bool:
        """
        Returns True if file for given process identifier is opened for reading.

        :param process_identifier: Process identifier.
        :return: True if file for given process identifier is opened for reading.
        """
        if process_identifier >= len(self._opened_files_for_reading):
            return False

        return self._opened_files_for_reading[process_identifier] is not None

    def __setitem__(self, global_identifier: int, data: str):
        """
        Stores given data.

        :param global_identifier: identifier that is unique for this data among all processes
         it is expected that the identifiers are consecutive numbers starting from 0
        :param data: Data to be stored in form of text line.
            Line separator will be added automatically.
        :raise ValueError: When there is already data stored under given identifier.
        """

        self.open()

        with self._storage_lock:
            if len(self._index) <= global_identifier:
                # we need to extend the index
                self._index.extend([None] * (global_identifier - len(self._index) + 1))

            if self._index[global_identifier] is not None:
                raise ValueError("Data with given identifier is already stored.")

            self._index[global_identifier] = (self._process_identifier, self._file.tell())
            print(data, file=self._file)
            self._stored_cnt.value += 1

            # check if we can update _waiting_for
            if global_identifier == self._waiting_for.value:
                self._waiting_for.value += 1
                while self._waiting_for.value < len(self) and self._index[self._waiting_for.value] is not None:
                    self._waiting_for.value += 1

    def __getitem__(self, global_identifier: int) -> str:
        """
        Returns data stored under given identifier.

        :param global_identifier: identifier that is unique for this data among all processes
        :return: Data stored under given identifier.
        :raise IndexError: When there is no data stored under given identifier.
        """

        with self._storage_lock:
            if len(self._index) <= global_identifier:
                raise IndexError(f"There is no data stored under {global_identifier} identifier.")

            index = self._index[global_identifier]
            if index is None:
                raise IndexError(f"There is no data stored under {global_identifier} identifier.")

            process_identifier, offset = index

            if not self._is_file_open_for_read(process_identifier):
                self._open_file_for_read(process_identifier)

            self._opened_files_for_reading[process_identifier].seek(offset)
            return self._opened_files_for_reading[process_identifier].readline().rstrip("\n").rstrip("\r")

    def __len__(self) -> int:
        """
        Returns number of stored data.

        :return: Number of stored data.
        """
        return self._stored_cnt.value

    def __iter__(self) -> Generator[str, None, None]:
        """
        Returns generator that yields all stored data and skips gaps.
        It will lock the storage for the time of iteration
        """

        with self._storage_lock:
            for i in range(len(self)):
                try:
                    yield self[i]
                except IndexError:
                    # gap
                    pass


