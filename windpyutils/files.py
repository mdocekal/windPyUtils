# -*- coding: UTF-8 -*-
""""
Created on 22.03.21
Utils for work with files.

:author:     Martin Dočekal
"""
import collections.abc
import csv
import json
import mmap
import multiprocessing
import os
import tempfile
from abc import ABC, abstractmethod
from contextlib import nullcontext
from dataclasses import dataclass, asdict, fields
from io import StringIO
from typing import Union, Dict, Any, Type, List, Optional, Sequence, MutableSequence, TextIO, Generator, Iterable, \
    TypeVar, Generic, Mapping, IO

C = TypeVar('C')  # type of line content


class BaseRandomLineAccessFile(collections.abc.Sequence, Generic[C], ABC):
    """
    Base class for all RandomLineAccessFiles these are files that allows to access line in file by its index.
    """

    def __init__(self, path_to: str, lines: Optional[MutableSequence[Union[int, str]]] = None):
        """
        initialization

        :param path_to: path to file
        :param lines: It may contain line offsets or line content in form of string representation.
            If None it will be created automatically.
            Allows selection of a subset of lines.
        """
        self.path_to = path_to
        self._dirty = False
        self._lines: MutableSequence[Union[int, str]] = [] if lines is None else lines

    @property
    def dirty(self) -> bool:
        """
        True means that the content differs from the one that is in original file.
        """
        return self._dirty

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
        return len(self._lines)

    def __iter__(self) -> Generator[C, None, None]:
        """
        sequence iteration over whole file
        :return: generator of lines
        """
        if self.closed:
            raise RuntimeError("Firstly open the file.")

        if self._dirty:
            for n in range(len(self)):
                yield self._get_item(n)
        else:
            self._file_seek(0)
            for n in range(len(self)):
                yield self._read_next_line()

    @abstractmethod
    def _file_seek(self, offset: int):
        """
        changes file offset

        :param offset: new offset
        :return:
        """
        pass

    @abstractmethod
    def open(self) -> "BaseRandomLineAccessFile":
        """
        Open the file if it was closed, else it is just empty operation.

        :return: Returns the object itself.
        :rtype: BaseRandomLineAccessFile
        """

        pass

    @abstractmethod
    def close(self):
        """
        Closes the file.
        """
        pass

    @property
    @abstractmethod
    def closed(self) -> bool:
        """
        Flag showing whether this file is closed.
        """
        pass

    def __getitem__(self, selector: Union[int, slice, Iterable]) -> Union[C, List[C]]:
        """
        Get n-th line from file.

        :param n: line index or slice
        :return: n-th line or list with lines subset in case of slice or iterable
        :raise RuntimeError: When the file is not opened.
        :raise IndexError: When the selector is invalid
        """
        if self.closed:
            raise RuntimeError("Firstly open the file.")

        if not isinstance(selector, int):
            iter_over = selector
            if isinstance(selector, slice):
                iter_over = range(len(self))[selector]
            return [self._get_item(i) for i in iter_over]

        return self._get_item(selector)

    def _get_item(self, n: int) -> str:
        """
        Get n-th line content.

        :param n: line index
        :return: n-th line
        """
        return self._read_line(n)

    @abstractmethod
    def _read_line(self, n: int) -> str:
        """
        Reads n-th line from file.

        :param n: line index
        :return: n-th line
        """
        pass

    @abstractmethod
    def _read_next_line(self) -> str:
        """
        Reads next line in file.

        :return: next line
        """
        pass


class RandomLineAccessFile(BaseRandomLineAccessFile[str]):
    """
    Allows fast access to any line in given file.
    This structure is just for reading.

    Makes line offsets index in advance.

    Example:

        with RandomLineAccessFile("example.txt") as lines:
            print(lines[150])
            print(lines[0])

    supports multi-processing

    :ivar path_to: path to file
    :vartype path_to: str
    :ivar file: file descriptor
    :vartype file: Optional[TextIO]
    """

    def __init__(self, path_to: str, line_offsets: Optional[Sequence[int]] = None):
        """
        initialization
        Makes just the line offsets index. Whole file itself is not loaded into memory.

        :param path_to: path to file
        :param line_offsets: Pre-created index of line offsets. If None it will be created automatically
        """

        super().__init__(path_to)
        self.file = None
        self._lines = line_offsets
        if line_offsets is None:
            self._index_file()
        self._opened_in_process_with_id = None

    def _index_file(self):
        """
        Makes index of line offsets.
        """

        self._lines = [0]

        with open(self.path_to, "rb") as f:
            while f.readline():
                self._lines.append(f.tell())

        del self._lines[-1]

    def open(self) -> "RandomLineAccessFile":
        """
        Open the file if it was closed, else it is just empty operation.

        :return: Returns the object itself.
        :rtype: RandomLineAccessFile
        """

        if self.file is None:
            self.file = open(self.path_to, "r")
            self._opened_in_process_with_id = os.getpid()

        return self

    def close(self):
        """
        Closes the file.
        """

        if self.file is not None:
            self.file.close()
            self.file = None
            self._opened_in_process_with_id = None

    def _reopen_if_needed(self):
        """
        Reopens itself if the multiprocessing is activated and this dataset was opened in parent process.
        """

        if self._opened_in_process_with_id is not None and os.getpid() != self._opened_in_process_with_id:
            # we don't want to open it when the file was not open yet to prevent accidental open
            self.close()
            self.open()

    @property
    def closed(self) -> bool:
        return self.file is None

    def _file_seek(self, offset: int):
        self._reopen_if_needed()
        self.file.seek(offset)

    def _read_line(self, n: int) -> str:
        self._file_seek(self._lines[n])
        return self._read_next_line()

    def _read_next_line(self) -> str:
        self._reopen_if_needed()
        return self.file.readline().rstrip("\n")


class MemoryMappedRandomLineAccessFile(RandomLineAccessFile):
    def __init__(self, path_to: str, line_offsets: Optional[Sequence[int]] = None):
        super().__init__(path_to, line_offsets)
        self.mm = None

    def open(self) -> "MemoryMappedRandomLineAccessFile":
        if self.file is None:
            self.file = open(self.path_to, "rb")
            self.mm = mmap.mmap(self.file.fileno(), 0, access=mmap.ACCESS_READ)
            self._opened_in_process_with_id = os.getpid()
        return self

    def close(self):
        if self.file is not None:
            self.mm.close()
            self.file.close()
            self.mm = None
            self.file = None
            self._opened_in_process_with_id = None

    def _file_seek(self, offset: int):
        self._reopen_if_needed()
        self.mm.seek(offset)

    def _read_line(self, n: int) -> str:
        self._file_seek(self._lines[n])
        return self._read_next_line()

    def _read_next_line(self) -> str:
        self._reopen_if_needed()
        return self.mm.readline().decode().rstrip("\n")


class BaseMutableRandomLineAccessFile(BaseRandomLineAccessFile, collections.abc.MutableSequence, ABC):
    """
    Base class for random line access file that acts like mutable sequence of lines.
    So it e.g. allows to change or append new lines.

    Those new/modified lines will not be immediately written to the file, but rather the changes will be done in memory
    which allows to make the work with a file more effective.
    You can save the file when you are done with changes.
    """

    def _get_item(self, n: int) -> str:
        """
        Determines whether the n-th line should be read from file or memory and returns it.

        :param n: line index
        :return: n-th line
        """
        line = self._lines[n]
        if isinstance(line, str):
            return line
        return self._read_line(n)

    def __setitem__(self, i: int, content: str):
        """
        change n-th line

        :param i: line index
        :param content: new content of a line
            It is not checked whether the content contains line separator and if it does in memory it acts like single
            line, but when the file is saved it becomes to act as multiple lines.
        :raise IndexError: When the key is invalid
        :raise ValueError: when invalid content is provided
        """
        if not isinstance(content, str):
            raise ValueError("You can set only string content.")
        self._dirty = True
        self._lines[i] = content

    def __delitem__(self, n: int):
        """
        remove n-th line

        :param n: index of line
        """
        self._dirty = True
        del self._lines[n]

    def insert(self, index: int, content: str):
        """
        insert new line at specified index

        :param index: index where the line should be inserted
        :param content: content of a line
        It is not checked whether the content contains line separator and if it does in memory it acts like single
            line, but when the file is saved it becomes to act as multiple lines.
        :raise ValueError: when invalid content is provided
        """
        if not isinstance(content, str):
            raise ValueError("You can insert only string content.")
        self._dirty = True
        self._lines.insert(index, content)

    def save(self, out: Union[str, TextIO], line_ending: str = "\n"):
        """
        Saves lines to given file.

        :param out: path to file or opened file
        :param line_ending: it allows to choose which line ending should be used
        """
        self._save_from_iter(self, out, line_ending)

    @staticmethod
    def _save_from_iter(lines: Iterable[str], out: Union[str, TextIO], line_ending: str = "\n"):
        """
        Saves lines to given file.

        :param lines: iterable of lines
        :param out: path to file or opened file
        :param line_ending: it allows to choose which line ending should be used
        """

        with (open(out, "w") if isinstance(out, str) else nullcontext()) as opened_f:
            f = opened_f if isinstance(out, str) else out

            for line in lines:
                line: str
                print(line.rstrip("\n"), file=f, end=line_ending)


class MutableRandomLineAccessFile(BaseMutableRandomLineAccessFile, RandomLineAccessFile):
    """
    Mutable variant of RandomLineAccessFile
    See :class:`.BaseMutableRandomLineAccessFile` for more information.


    Example:
        >>>with MutableRandomLineAccessFile("example.txt") as file:
        >>>    print(file[1])
        "content on line index 1"
        >>>    file[1] = "New line content"
        >>>    print(file[1])
        "New line content"
        >>>    file.save("results.txt")

    multiprocessing is NOT supported
    """
    pass


class MutableMemoryMappedRandomLineAccessFile(BaseMutableRandomLineAccessFile, MemoryMappedRandomLineAccessFile):
    """
    Mutable variant of MemoryMappedRandomLineAccessFile
    See :class:`.BaseMutableRandomLineAccessFile` for more information.

    Example:
        >>>with MutableMemoryMappedRandomLineAccessFile("example.txt") as file:
        >>>    print(file[1])
        "content on line index 1"
        >>>    file[1] = "New line content"
        >>>    print(file[1])
        "New line content"
        >>>    file.save("results.txt")

    multiprocessing is NOT supported
    """

    pass


class Record(ABC):
    """
    Abstract class of a record that forces load/save interface.
    """
    _class_fields_cache = {}
    _class_fields_types_cache = {}

    @classmethod
    def field_names(cls) -> List[str]:
        """
        Record field names.
        """

        try:
            return cls._class_fields_cache[cls]
        except KeyError:
            cls._class_fields_cache[cls] = [f.name for f in fields(cls) if f.init]
            return cls._class_fields_cache[cls]

    @classmethod
    def field_types(cls) -> List[Type]:
        """
        Record field types.
        """

        try:
            return cls._class_fields_types_cache[cls]
        except KeyError:
            cls._class_fields_types_cache[cls] = [f.type for f in fields(cls) if f.init]
            return cls._class_fields_types_cache[cls]

    @classmethod
    @abstractmethod
    def load(cls, s: str) -> "Record":
        """
        Loads record from its string representation.

        :param s: string representation
        :return: loaded record
        """
        pass

    @abstractmethod
    def save(self) -> str:
        """
        Converts record to its string representation that can be later loaded.
        WARNING: It should not contain line endings as we are assuming single record per line.

        This could be empty operation when it is used with non-mutable files.
        :return: representation of a record that could be loaded
        """
        pass


@dataclass
class JsonRecord(Record, ABC):
    """
    Record with json string representation.
    """

    @classmethod
    def load(cls, s: str) -> "JsonRecord":
        dict_repr = json.loads(s)
        arg_dict = {k: v for k, v in dict_repr.items() if k in cls.field_names()}
        return cls(**arg_dict)

    def save(self) -> str:
        return json.dumps(asdict(self), separators=(',', ':'))


@dataclass
class CSVRecord(Record, ABC):
    """
    Record with csv string representation.
    """
    _delimiter = ","
    _res_io = StringIO()
    _writer = {}

    @classmethod
    def _dict_to_string(cls, d: Dict) -> str:
        """
        Converts dict representation to string.

        :param d: dictionary containing all fields
        :return: string representation of dictionary
        """
        try:
            writer = cls._writer[cls]
        except KeyError:
            writer = csv.DictWriter(cls._res_io, fieldnames=cls.field_names(), delimiter=cls._delimiter)
            cls._writer[cls] = writer

        writer.writerow(d)

        res = cls._res_io.getvalue()
        cls._res_io.truncate(0)
        cls._res_io.seek(0)
        return res

    @classmethod
    def load(cls, s: str) -> "CSVRecord":
        list_repr = next(iter(csv.reader([s], delimiter=cls._delimiter)))
        arg_dict = {k: t(v) for k, t, v in zip(cls.field_names(), cls.field_types(), list_repr)}
        return cls(**arg_dict)

    def save(self) -> str:
        return self._dict_to_string(asdict(self))


@dataclass
class TSVRecord(CSVRecord, ABC):
    """
    Record with tsv string representation.
    """
    _delimiter = "\t"


R = TypeVar('R', bound=Record)  # type of record content


class BaseRecordFile(BaseRandomLineAccessFile[Record], Generic[R], ABC):
    """
    Base class for record files that acts like a sequence. It allows direct reading/writing of structured data
    (records).
    """

    def __init__(self, path_to: str, record_class: Type[R],
                 lines: Optional[MutableSequence[Union[int, str]]] = None):
        """
        initialization

        :param path_to: path to source file
        :param record_class: class of a records that are saved (or should be) on given path
        :param lines: It may contain line offsets or line content in form of string representation.
            If None it will be created automatically.
            Allows selection of a subset of lines.
        """
        super().__init__(path_to, lines)
        self._dirty = True
        self.record_class = record_class

    def _get_item(self, n: int) -> R:
        """
        Determines whether the n-th line should be read from file or memory and returns it.

        :param n: line index
        :return: n-th line
        """
        line = super()._get_item(n)
        return self.record_class.load(line)


class BaseMutableRecordFile(BaseRecordFile, BaseMutableRandomLineAccessFile, ABC):
    """
    Base class for record files that acts like a mutable sequence. It allows direct reading/writing of structured data
    (records).
    """

    def __setitem__(self, i: int, r: R):
        """
        change n-th line

        :param i: line index
        :param r: record
        :raise IndexError: When the key is invalid
        :raise ValueError: when invalid content is provided
        """
        if not isinstance(r, self.record_class):
            raise ValueError("You can set only Record.")

        super().__setitem__(i, r.save())

    def insert(self, index: int, content: R):
        """
        insert new line at specified index

        :param index: index where the line should be inserted
        :param content: record
        :raise ValueError: when invalid content is provided
        """
        if not isinstance(content, self.record_class):
            raise ValueError("You can set only Record.")

        super().insert(index, content.save())

    def save(self, out: Union[str, TextIO], line_ending: str = "\n"):
        """
        Saves lines to given file.

        :param out: path to file or opened file
        :param line_ending: it allows to choose which line ending should be used
        """

        self._save_from_iter(
            (BaseRandomLineAccessFile._get_item(self, i) if isinstance(x, int) else x
             for i, x in enumerate(self._lines)),
            out,
            line_ending
        )


class RecordFile(BaseRecordFile, RandomLineAccessFile, Generic[R]):
    """
    Record file that acts like sequence. It allows direct reading of structured data (records).

    Example:
        >>>with RecordFile("example.txt", MyRecord) as file:
        >>>    print(file[1])
        "MyRecord(some=10,arg=2)"

    """
    pass


class MutableRecordFile(BaseMutableRecordFile, MutableRandomLineAccessFile, Generic[R]):
    """
    Record file that acts like mutable sequence. It allows direct reading/writing of structured data (records).


    Example:
        >>>with MutableRecordFile("example.txt", MyRecord) as file:
        >>>    print(file[1])
        "MyRecord(some=10,arg=2)"
        >>>    file[1] = MyRecord(some=5,arg=2)
        >>>    print(file[1])
        "MyRecord(some=5,arg=2)"
        >>>    file.save("results.txt")
    """
    pass


class MemoryMappedRecordFile(BaseRecordFile, MemoryMappedRandomLineAccessFile, Generic[R]):
    """
    Memory mapped record file that acts like sequence. It allows direct reading of structured data (records).

    Example:
        >>>with MemoryMappedRecordFile("example.txt", MyRecord) as file:
        >>>    print(file[1])
        "MyRecord(some=10,arg=2)"
    """
    pass


class MutableMemoryMappedRecordFile(BaseMutableRecordFile, MutableMemoryMappedRandomLineAccessFile, Generic[R]):
    """
    Memory mapped record file that acts like mutable sequence. It allows direct reading/writing of structured data
    (records).

    Example:
        >>>with MutableMemoryMappedRecordFile("example.txt", MyRecord) as file:
        >>>    print(file[1])
        "MyRecord(some=10,arg=2)"
        >>>    file[1] = MyRecord(some=5,arg=2)
        >>>    print(file[1])
        "MyRecord(some=5,arg=2)"
        >>>    file.save("results.txt")
    """
    pass


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

    multiprocessing is supported

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
        self._opened_in_process_with_id = None

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
            self._opened_in_process_with_id = os.getpid()
        return self

    def close(self):
        """
        Closes the file.
        """

        if self.file is not None:
            self.file.close()
            self.file = None
            self._opened_in_process_with_id = None

    def _reopen_if_needed(self):
        """
        Reopens itself if the multiprocessing is activated and this dataset was opened in parent process.
        """

        if self._opened_in_process_with_id is not None and os.getpid() != self._opened_in_process_with_id:
            # we don't want to open it when the file was not open yet to prevent accidental open
            self.close()
            self.open()

    def __getitem__(self, k) -> str:
        """
        Get the line by key.

        :param k: key of line in file
        :return: key of a line
        :raise RuntimeError: When the file is not opened.
        """
        if self.file is None:
            raise RuntimeError("Firstly open the file.")
        self._reopen_if_needed()
        self.file.seek(self.mapping[k])
        return self.file.readline()


class TmpPool:
    """
    Structure for managing tmp files.

    Example:
        >>> with TmpPool() as pool:
        >>>    pool.create()
        path to created tmp file
    """

    def __init__(self, d: Optional[str] = None, multi_proc: bool = False):
        """
        initializes pool
        :param d: directory where the tmp files will be created or the dafault is used
        :param multi_proc: Pass true if you want to use that with multiple processes
        """

        self._d = d
        self._created_files = []
        self._multi_proc = multi_proc
        self._manager = None
        if multi_proc:
            self._manager = multiprocessing.Manager()

    def __len__(self):
        return len(self._created_files)

    def __getitem__(self, item) -> str:
        """
        Path to tmp file.

        :param item: index of tmp file.
        :return: path to tmp file
        """
        return self._created_files[item]

    def __enter__(self):
        if self._multi_proc:
            self._manager = multiprocessing.Manager().__enter__()
            self._created_files = self._manager.list()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()
        if self._manager is not None:
            self._manager.__exit__(None, None, None)

    def create(self) -> str:
        """
        Create tmp file.
        :return: Path to tmp file
        """
        tmp = tempfile.NamedTemporaryFile(delete=False, dir=self._d)
        tmp.close()
        self._created_files.append(tmp.name)
        return tmp.name

    def remove(self, p: str):
        """
        Removes file from file system and also from its pool.
        :param p: path to tmp file
        """
        try:
            os.remove(p)
        except FileNotFoundError:
            # already removed
            pass

        self._created_files.remove(p)

    def flush(self):
        """
        Removes all created files from this pool and also the file system.
        """
        for p in self._created_files:
            try:
                os.remove(p)
            except FileNotFoundError:
                # already removed
                pass

        self._created_files = self._manager.list() if self._multi_proc else []


class FilePool(Mapping[str, IO]):
    """
    Pool of files. It is used to open and close multiple files simultaneously by one shared context manager.
    """

    def __init__(self, files: Iterable[str], mode: str = "r"):
        """
        Create new file pool.

        :param files: iterable of file path
        :param mode: mode in which files will be opened
        """
        self._files = files
        self._mode = mode
        self.file_handles = None

    def __enter__(self) -> "FilePool":
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):
        if self.file_handles is None:
            raise RuntimeError("Firstly open the pool.")
        return iter(self.file_handles)

    def __len__(self):
        if self.file_handles is None:
            raise RuntimeError("Firstly open the pool.")
        return len(self.file_handles)

    def __getitem__(self, path: str):
        """
        Get file handle associated to given path.

        :param path: path to file
        :return: file handle
        :raises KeyError: if file is not in pool
        """
        if self.file_handles is None:
            raise RuntimeError("Firstly open the pool.")

        return self.file_handles[path]

    def open(self) -> "FilePool":
        """
        Open all files in pool.

        :return: self
        """
        self.file_handles = {f: open(f, self._mode) for f in self._files}
        return self

    def close(self):
        """
        Close all files in pool.
        """
        for f in self.file_handles.values():
            f.close()

        self.file_handles = None
