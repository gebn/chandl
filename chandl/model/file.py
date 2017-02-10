# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os
import binascii
import base64
import six
import requests
import shutil

from chandl import util


TYPE_VIDEO = ['webm', 'gif']
TYPE_IMAGE = ['jpg', 'png']

# passable via the CLI's --filter option
_FILTERS = {
    'videos': TYPE_VIDEO,
    'images': TYPE_IMAGE
}

logger = logging.getLogger(__name__)


def expand_filters(filters):
    """
    Expand a list of file filters passed on the command line. Each item could be
    a csv or single file extension, or key in the _FILTERS dict above, in which
    case it needs to be expanded into file extensions. Examples:

        ['jpg', 'webm'] -> jpg, webm
        ['jpg, webm', 'png'] -> jpg, webm, png
        ['webm,images'] -> webm, jpg, png

    :param filters: The list of filters from argparse.
    :return: A set of file extensions.
    """
    extensions = set()

    for arg in filters:  # "videos, jpg"
        for type_ in [s.strip() for s in arg.split(',')]:  # "videos"|"jpg"
            if type_ in _FILTERS:  # "videos"
                for ext in _FILTERS[type_]:
                    # return each extension in that category
                    extensions.add(ext)
            else:  # "jpg"
                # it's a file extension - just return it
                extensions.add(type_)

    return extensions


@six.python_2_unicode_compatible
class File:
    """
    Represents a media file attached to a post.
    """

    def __init__(self, id_, board, name, extension, size, width, height, md5):
        """
        Initialise a new file instance.

        :param id_: A unique identifier for the file: it's UNIX timestamp
                    prepended to the number of milliseconds.
        :param board: The board this file was posted in, e.g. 'wg'.
        :param name: The original name of the file.
        :param extension: The file's extension, without leading dot.
        :param size: The size of the file in bytes.
        :param width: The width of the media in pixels.
        :param height: The height of the media in pixels.
        :param md5: The MD5 hash of the file as a 32-character lowercase string.
        """
        self.id = id_
        self.board = board
        self.name = name
        self.extension = extension
        self.size = size
        self.width = width
        self.height = height
        self.md5 = md5

    @property
    def filename(self):
        """
        Get the name of this file as it appears on the 4chan website.

        :return: This file's id with extension.
        """
        return six.u(str(self.id)) + '.' + self.extension

    @property
    def url(self):
        """
        Retrieve the URL where this file can be downloaded.

        :return: The URL.
        """
        return 'https://i.4cdn.org/{0}/{1}'.format(self.board, self.filename)

    def save_to(self, directory, name, verify=True, session=None):
        """
        Download and save this file.

        :param directory: The directory to save this file within.
        :param name: The file name to save under.
        :param verify: Whether to verify the file's checksum once it is written.
                       Defaults to true.
        :param session: The requests session to use for this download. If
                        omitted, a new session will be used.
        :raise IOError: If the file could not be downloaded, written, or if
                        `verify` was enabled and its checksum did not match the
                        one reported by 4chan.
        """
        destination = os.path.join(directory, name)

        if os.path.isfile(destination) and \
                util.md5_file(destination) == self.md5:
            logger.debug('%s already exists; skipping download', self)
            return

        logger.debug('Downloading %s', self)
        if not session:
            session = util.create_session()
        response = session.get(self.url, stream=True)
        if response.status_code != requests.codes.ok:
            raise IOError('File failed to download with status {0}'.format(
                response.status_code))

        with open(destination, 'wb') as handle:
            shutil.copyfileobj(response.raw, handle)

        if verify and util.md5_file(destination) != self.md5:
            raise IOError('Verify failed: checksum mismatch')

    @staticmethod
    def parse_json(board, json):
        """
        Create a file object from 4Chan's API format.

        :param board: The name of the board this file was uploaded to, e.g.
                      'wg'.
        :param json: The JSON of the post containing this file.
        :return: The created file instance.
        :raises ValueError: If the post does not contain an image.
        """

        def unpack_hash(encoded):
            """
            Unpacks a packed, base64 encoded MD5 checksum.
            :param encoded: The unicode representation of the encoded checksum.
            :return: The unicode representation of the unpacked, 32-character
                     checksum.
            """
            return binascii.hexlify(
                base64.b64decode(encoded.encode('ascii'))).decode('ascii')

        if 'filename' not in json:
            raise ValueError('Post does not contain an image')

        return File(json['tim'], board, util.unescape_html(json['filename']),
                    json['ext'][1:], json['fsize'], json['w'], json['h'],
                    unpack_hash(json['md5']).rstrip())

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
               other.__dict__ == self.__dict__

    def __str__(self):
        return 'File({0}, {1}.{2}, {3}, {4}x{5})'.format(
            self.id, self.name, self.extension, util.bytes_fmt(self.size),
            self.width, self.height)
