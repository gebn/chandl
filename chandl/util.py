# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import sys
import hashlib
import unidecode


def bytes_fmt(num, suffix='B'):
    """
    Turn a number of bytes into a more friendly representation, e.g. 2.5MiB.

    :param num: The number of bytes to convert.
    :param suffix: The unit suffix (defaults to 'B').
    :return: The human-readable equivalent of the input size.
    :raises ValueError: If num is the wrong type.
    """

    if not isinstance(num, int):
        raise ValueError('Byte count must be an integer')

    num = abs(num)
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if num < 1024.0:
            return '{0:.1f} {1}{2}'.format(num, unit, suffix)
        num /= 1024.0
    return '{0:.1f} {1}{2}'.format(num, 'Yi', suffix)


def decode_cli_arg(arg):
    """
    Turn a bytestring provided by `argparse` into unicode.

    :param arg: The bytestring to decode.
    :return: The argument as a unicode object.
    :raises ValueError: If arg is None.
    """

    if arg is None:
        raise ValueError('Argument cannot be None')

    return arg.decode(sys.getfilesystemencoding())


def make_filename(string):
    """
    Turn a string into something that can be safely used as a file or directory
    name.

    :param string: The string to convert.
    :return: The sanitised string.
    :raises ValueError: If string is None.
    """

    if string is None:
        raise ValueError('String cannot be None')

    safe = [' ', '.', '_', ':']
    joined = ''.join([c for c in unidecode.unidecode(string)
                      if c.isalnum() or c in safe]).strip()
    if not joined:
        raise ValueError('Filename would be empty')
    return joined


def md5_file(path):
    """
    Get the MD5 hash of a file.

    :param path: The path of the file.
    :return: The 32-character long lowercase hex representation of the
             checksum.
    :raises ValueError: If path is invalid.
    """

    if not path:
        raise ValueError('Path cannot be empty or None')

    hash_ = hashlib.md5()
    with open(path, 'rb') as fd:
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
