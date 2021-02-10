# -*- coding: UTF-8 -*-
""""
Created on 27.01.21

Module containing buffers.

:author:     Martin Dočekal
"""
from typing import TextIO


class PrintBuffer:
    """
    Stores and prints data marked with serial numbers in sorted order.

    Use unique serial numbers else the data will be overwritten.

    Usage:

        pBuffer = PrintBuffer()
        pBuffer.print(1, "B")   # stores B because the next printed string should have serial number 0
        pBuffer.print(2, "C")   # stores C because the next printed string should have serial number 0
        pBuffer.print(0, "A")   # prints
        ->  A
            B
            C
        pBuffer.print(3, "C")  # print immediately because 3 is the next serial number
        ->  C

    :var file_out: Where the output should be printed.
    :var print_flush: flush parameter for print method
    :var end: String appended to the last character before print. Default is a newline.
    """

    def __init__(self, file_out: TextIO, print_flush: bool = False, end: str = "\n"):
        """
        initialization of buffer

        :param file_out: Where the output should be printed.
        :type file_out: TextIO
        :param print_flush: flush parameter for print method
        :type print_flush: bool
        :param end: String appended to the last character before print. Default is a newline.
        :type end: str
        """
        self._waiting_for = 0
        self._buffer = {}
        self.fileOut = file_out
        self.printFlush = print_flush
        self.end = end

    def _print(self, value: str):
        """
        Just wrapper for print.

        :param value: Value that should be printed.
        :type value: str
        """
        print(value, file=self.fileOut, flush=self.printFlush, end=self.end)

    @property
    def waiting_for(self) -> int:
        """
        Serial number the buffer is waiting for.
        """
        return self._waiting_for

    def print(self, serial_number: int, value: str) -> bool:
        """
        Prints value if serial number is the one it is waiting for, else stores that value for later.
        If serial number is the one it is waiting for and it also has stored values with consequent serial numbers
        it will print them too.

        Use unique serial numbers else the data will be overwritten.

        :param serial_number: Serial number of actual value.
        :type serial_number: int
        :param value: String that can be printed.
        :type value: str
        :return: True if value (or multiple values) was printed. False when the value was buffered.
        :rtype: bool
        """

        if serial_number == self._waiting_for:
            self._print(value)

            self._waiting_for += 1

            while self._waiting_for in self._buffer:
                self._print(self._buffer[self._waiting_for])
                del self._buffer[self._waiting_for]
                self._waiting_for += 1

            return True
        else:
            self._buffer[serial_number] = value
            return False

    def flush(self):
        """
        Prints out all data stored in buffer in ascending sorted order according to their serial number.

        Sets the waitingFor to the next serial number after the biggest one in memory.
        Do nothing if buffer is empty.
        """
        serial_number = self._waiting_for - 1  # will guarantee that if the buffer is empty the waitingFor does not change

        for serial_number in sorted(self._buffer.keys()):
            self._print(self._buffer[serial_number])
            del self._buffer[serial_number]

        self._waiting_for = serial_number + 1

    def __len__(self):
        """
        Number of stored items.
        """

        return len(self._buffer)

    def clear(self):
        """
        Clears buffer without printing items inside and set waitingFor to zero.
        """
        self._buffer = {}
        self._waiting_for = 0
