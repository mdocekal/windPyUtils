# -*- coding: UTF-8 -*-
""""
Created on 05.02.21
Visualization tools for text environment.

:author:     Martin Dočekal
"""
import math
import sys
from typing import Dict, TextIO, Tuple, Sequence, Optional


def print_histogram(bars: Sequence[Tuple[str, float]], max_width: int = 40, file: Optional[TextIO] = None,
                    bar_char: str = "█", print_value: bool = True):
    """
    Prints histogram defined by the provided bars.

    Example:
        >>> print_histogram([("red", 10), ("green", 5), ("blue", 7)])
        red   ████████████████████████████████████████ 10
        green ████████████████████ 5
        blue  ████████████████████████████ 7

    :param bars: It's sequence of bars. Bar is a tuple. Tuple defines label and value associated with it.
        Value must be always non negative.
    :type bars: Sequence[Tuple[str, float]]
    :param max_width: Maximal number of bar_chars that represents histogram bar.
    :type max_width: int
    :param file: Prints results to this output.
    :type file: Optional[TextIO]
    :param bar_char: Character (or multiple) that will be used for creating representation of a bar.
    :type bar_char: str
    :param print_value: If true prints value after the bar.
    :type print_value: True
    :raise AssertionError: On invalid max_width.
    :raise ValueError: When a value is negative.
    """
    if file is None:
        file = sys.stdout

    max_label_chars = 0
    max_value = - math.inf

    for label, value in bars:
        if len(label) > max_label_chars:
            max_label_chars = len(label)
        if value < 0:
            raise ValueError(f"The value {value} for label {label} is negative.")
        if value > max_value:
            max_value = value

    for label, value in bars:
        formatting_spaces = " " * (max_label_chars - len(label))
        bar = bar_char * (round(max_width * value / max_value))

        print(f"{label}{formatting_spaces} {bar}{' ' + str(value) if print_value else ''}", file=file)


def print_buckets_histogram(values: Dict[float, float], buckets: int = -1, bucket_size_int: bool = False,
                            max_width: int = 40, file: Optional[TextIO] = None, bar_char: str = "█",
                            print_value: bool = True, decimals: int = 2):
    """
    Prints histogram defined by the provided dictionary the x values are the keys and y values are the dictionary values
    for given key. The keys will be automatically sorted into buckets if buckets > 0. Each bucket is associated with one
    histogram bar.

    The bar label will the associated key in case when buckets == -1, else it will be the buckets interval.

    Example:
        >>> print_buckets_histogram({0:2,5:8, 10:18, 15:8, 20:2}, buckets=1)
        [0,20] ████████████████████████████████████████ 38

        >>> print_buckets_histogram({0:2,5:8, 10:18, 15:8, 20:2}, buckets=3)
        [0,6.67)     ██████████████████████ 10
        [6.67,13.33) ████████████████████████████████████████ 18
        [13.33,20]   ██████████████████████ 10

        >>> print_buckets_histogram({0:2,5:8, 10:18, 15:8, 20:2}, buckets=5)
        [0,4)   ████ 2
        [4,8)   ██████████████████ 8
        [8,12)  ████████████████████████████████████████ 18
        [12,16) ██████████████████ 8
        [16,20] ████ 2

        >>> print_buckets_histogram({0:2,5:8, 10:18, 15:8, 20:2})
        0  ████ 2
        5  ██████████████████ 8
        10 ████████████████████████████████████████ 18
        15 ██████████████████ 8
        20 ████ 2

    :param values: Dictionary that defines the x,y coordinates for the histogram.
    :type values: Dict[float, float]
    :param buckets: Number of histogram buckets. Its maximal number of buckets if there would be a single key value
    then only one bucket will be created even though buckets would be equal to 10.
        -1 means that number of buckets should be equal to number of keys in values dict
    :type buckets: int
    :param bucket_size_int: If true bucket size will be rounded up to nearest integer (just for buckets > 0).
        May cause that the last bucket interval will end after max.
    :type bucket_size_int: bool
    :param max_width: Maximal number of characters that represents histogram bar.
    :type max_width: int
    :param file: Prints results to this output.
    :type file: Optional[TextIO]
    :param bar_char: Character (or multiple) that will be used for creating representation of a bar.
    :type bar_char: str
    :param print_value: If true prints value after the bar.
    :type print_value: True
    :param decimals: Float numbers will be rounded to x decimal points.
    :type decimals: int
    :raise AssertionError: On invalid number of buckets, on invalid max_width or empty values dict.
    :raise ValueError: When a value in bucket is negative.
    """

    assert buckets == -1 or buckets > 0
    assert len(values) > 0

    if buckets == -1 or len(values) == 1:
        # buckets are already defined
        print_histogram([(str(label), val) for label, val in sorted(values.items(), key=lambda ite: ite[0])],
                        max_width, file, bar_char, print_value)
    else:
        # we need to sort keys into buckets
        min_k = min(values.keys())
        max_k = max(values.keys())
        keys_spread = max_k - min_k
        bucket_size = keys_spread / buckets
        if bucket_size_int:
            bucket_size = math.ceil(bucket_size)

        hist = [0] * buckets

        for k, v in values.items():
            belongs_to_bucket = int((k - min_k) / bucket_size)
            if belongs_to_bucket == buckets:  # only when the k is max
                # the last bucket interval is closed and we have max value so it belongs to the las bucket
                belongs_to_bucket -= 1

            hist[belongs_to_bucket] += v

        bucket_labels = []
        bucket_start = min_k
        for bucket_offset in range(len(hist) - 1):  # the last one is handled separately
            bucket_end = bucket_start + bucket_size
            str_s = f"{bucket_start:.{decimals}f}".rstrip("0").rstrip(".")
            str_e = f"{bucket_end:.{decimals}f}".rstrip("0").rstrip(".")
            bucket_labels.append(f"[{str_s},{str_e})")
            bucket_start = bucket_end

        # the last one is closed interval to the max value
        bucket_end = max_k
        if bucket_size_int:
            bucket_end = math.ceil(bucket_end)

        str_s = f"{bucket_start:.{decimals}f}".rstrip("0").rstrip(".")
        str_e = f"{bucket_end:.{decimals}f}".rstrip("0").rstrip(".")
        bucket_labels.append(f"[{str_s},{str_e}]")

        print_histogram([(label, val) for label, val in zip(bucket_labels, hist)],
                        max_width, file, bar_char, print_value)
