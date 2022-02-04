# -*- coding: UTF-8 -*-
""""
Created on 22.03.21
Utils for work with files.

:author:     Martin Dočekal
"""
import csv
from typing import Union, Dict, Any, Type


class RandomLineAccessFile:
    """
    Allows fast access to any line in given file.
    This structure is just for reading.

    Makes line offsets index in advance.

    Example:

        with RandomLineAccessFile("example.txt") as lines:
            print(lines[150])
            print(lines[0])

    :ivar path_to: path to file
    :vartype path_to: str
    :ivar file: file descriptor
    :vartype file: Optional[TextIO]
    """

    def __init__(self, path_to: str):
        """
        initialization
        Makes just the line offsets index. Whole file itself is not loaded into memory.

        :param path_to: path to file
        """

        self.path_to = path_to
        self.file = None
        self._line_offsets = None
        self._index_file()

    def _index_file(self):
        """
        Makes index of line offsets.
        """

        self._line_offsets = [0]

        with open(self.path_to, "rb") as f:
            while f.readline():
                self._line_offsets.append(f.tell())

        del self._line_offsets[-1]

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __len__(self) -> int:
        """
        Number of lines in the file.

        :return: Number of lines in the file.
        """
        return len(self._line_offsets)

    def open(self) -> "RandomLineAccessFile":
        """
        Open the file if it was closed, else it is just empty operation.

        :return: Returns the object itself.
        :rtype: RandomLineAccessFile
        """

        if self.file is None:
            self.file = open(self.path_to, "r")
        return self

    def close(self):
        """
        Closes the file.
        """

        if self.file is not None:
            self.file.close()
            self.file = None

    def __getitem__(self, n) -> str:
        """
        Get n-th line from file.

        :param n: line index
        :return: n-th line
        :raise RuntimeError: When the file is not opened.
        """
        if self.file is None:
            raise RuntimeError("Firstly open the file.")

        self.file.seek(self._line_offsets[n])
        return self.file.readline()


class MapAccessFile:
    """
    Allows fast access to any line in given file indexed by given mapping.
    This structure is just for reading.

    Example with dict:
        >>>with MapAccessFile("example.txt", {"car": 0, "boat": 123}) as map_file:
        >>>    print(map_file["car"])

    Example with index file containing previous dict in tsv:
        >>>with MapAccessFile("example.txt", "example.index") as map_file:
        >>>    print(map_file["car"])

    :ivar path_to: path to file
    :vartype path_to: str
    :ivar file: file descriptor
    :vartype file: Optional[TextIO]
    :ivar mapping: mapping used for given file:
        key->line offset
    :vartype mapping: Dict[Any, int]
    """

    def __init__(self, path_to: str, mapping: Union[Dict[Any, int], str], key_type: Type = str):
        """
        initialization
        Whole file itself is not loaded into memory.

        :param path_to: path to file
        :param mapping: defines mapping that is used for access
            You can provide a dict in form of
                your key -> file offset to the beginning of a line
            Or path to file with index in tsv format with following header:
                key\tfile_line_offset
        :param key_type: type of a key in mapping useful when the mapping is loaded from file
        """

        self.path_to = path_to
        self.file = None
        self.mapping = self.load_mapping(mapping, key_type) if isinstance(mapping, str) else mapping

    @staticmethod
    def load_mapping(p: str, t: Type = str) -> Dict[Any, int]:
        """
        Method for loading key->line offset mapping from tsv file with header key\tfile_line_offset.

        :param p: path to tsv file
        :param t: type of the key
        :return: the mapping
        """
        res = {}
        with open(p, newline='') as f:
            for r in csv.DictReader(f, delimiter="\t"):
                res[t(r["key"])] = int(r["file_line_offset"])

        return res

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __len__(self) -> int:
        """
        Number of mapped lines in the file.

        :return: Number of mapped lines in the file.
        """
        return len(self.mapping)

    def open(self) -> "MapAccessFile":
        """
        Open the file if it was closed, else it is just empty operation.

        :return: Returns the object itself.
        :rtype: RandomLineAccessFile
        """

        if self.file is None:
            self.file = open(self.path_to, "r")
        return self

    def close(self):
        """
        Closes the file.
        """

        if self.file is not None:
            self.file.close()
            self.file = None

    def __getitem__(self, k) -> str:
        """
        Get the line by key.

        :param k: key of line in file
        :return: key of a line
        :raise RuntimeError: When the file is not opened.
        """
        if self.file is None:
            raise RuntimeError("Firstly open the file.")

        self.file.seek(self.mapping[k])
        return self.file.readline()
