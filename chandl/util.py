# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import sys
import hashlib
import unidecode
import six
import requests

import chandl


def bytes_fmt(num, suffix='B'):
    """
    Turn a number of bytes into a more friendly representation, e.g. 2.5MiB.

    :param num: The number of bytes to convert.
    :param suffix: The unit suffix (defaults to 'B').
    :return: The human-readable equivalent of the input size.
    :raises ValueError: If num is not an integer.
    """
    if not isinstance(num, six.integer_types):
        raise ValueError('Byte count must be an integral type')

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

    if sys.version_info.major == 3:
        # already decoded
        return arg

    return arg.decode(sys.getfilesystemencoding())


def expand_cli_args(args):
    """
    Expand a list of possibly comma separated arguments, removing duplicates.

    :param args: The list of arguments to expand.
    :return: The set of unique arguments.
    """
    items = set()
    for arg in args:  # "a.jpg,b.png"
        for arg_ in [n.strip() for n in arg.split(',')]:  # "a.jpg"|"b.jpg"
            items.add(arg_)
    return items


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

    safe = [' ', '.', '_', '-', '\'']
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


def create_session():
    """
    Create a requests session for issuing HTTP requests to 4chan.

    :return: The created session.
    """
    headers = requests.utils.default_headers()
    headers.update({
        'User-Agent': 'chandl/' + chandl.__version__
    })

    session = requests.Session()
    session.headers = headers
    return session


def unescape_html(html_):
    """
    Replace HTML entities (e.g. `&pound;`) in a string.

    :param html_: The escaped HTML.
    :return: The input string with entities replaces.
    """

    # http://stackoverflow.com/a/2360639

    if sys.version_info.major == 2:  # 2.7
        # noinspection PyUnresolvedReferences,PyCompatibility
        from HTMLParser import HTMLParser
        return HTMLParser().unescape(html_)

    if sys.version_info.minor == 3:  # 3.3
        # noinspection PyCompatibility
        from html.parser import HTMLParser
        # noinspection PyDeprecation
        return HTMLParser().unescape(html_)

    # 3.4+
    # noinspection PyCompatibility
    import html
    return html.unescape(html_)
