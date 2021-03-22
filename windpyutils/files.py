# -*- coding: UTF-8 -*-
""""
Created on 22.03.21
Utils for work with files.

:author:     Martin Dočekal
"""


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
