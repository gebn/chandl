# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import sys
import hashlib


def bytes_fmt(num, suffix='B'):
    """
    Turn a number of bytes into a more friendly representation, e.g. 2.5MiB.

    :param num: The number of bytes to convert.
    :param suffix: The unit suffix (defaults to 'B').
    :return: The human-readable equivalent of the input size.
    """

    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return '{0:.1f} {1}{2}'.format(num, unit, suffix)
        num /= 1024.0
    return '{0:.1f} {1}{2}'.format(num, 'Yi', suffix)


def decode_cli_arg(arg):
    """
    Turn a bytestring provided by `argparse` into unicode.

    :param arg: The bytestring to decode.
    :return: The argument as a unicode object.
    """
    return arg.decode(sys.getfilesystemencoding())


def make_filename(string):
    """
    Turn a string into something that can be safely used as a file or directory
    name.

    :param string: The string to convert.
    :return: The sanitised string.
    """

    safe = [' ', '.', '_', ':']
    return ''.join(c for c in string if c.isalnum() or c in safe).rstrip()


def md5_file(path):
    """
    Get the MD5 hash of a file.

    :param path: The path of the file.
    :return: The 32-character long lowercase hex representation of the
             checksum.
    """

    hash_ = hashlib.md5()
    with open(path, 'r') as fd:
        for chunk in iter(lambda: fd.read(4096), b''):
            hash_.update(chunk)
    return hash_.hexdigest()


def log_level_from_vebosity(verbosity):
    """
    Get the `logging` module log level from a verbosity.

    :param verbosity: The number of times the `-v` option was specified.
    :return: The corresponding log level.
    """

    if verbosity == 0:
        return logging.WARNING
    if verbosity == 1:
        return logging.INFO
    return logging.DEBUG
