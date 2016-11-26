# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os
import sys
import binascii
import base64
import six
from six.moves.urllib import request

from chandl import util


logger = logging.getLogger(__name__)

TYPE_VIDEO = ['webm', 'gif']
TYPE_IMAGE = ['jpg', 'png']


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
        :param board: The board this file was posted in, e.g. 'gif'.
        :param name: The original name of the file.
        :param extension: The file's extension, without leading dot.
        :param size: The size of the file in bytes.
        :param width: The width of the media in pixels.
        :param height: The height of the media in pixels.
        :param md5: The MD5 hash of the file as a 32-character string.
        """

        self.id = id_
        self.board = board
        self.name = name[:30]  # the length of some file names causes problems
        self.extension = extension
        self.size = size
        self.width = width
        self.height = height
        self.md5 = md5

    @property
    def url(self):
        """
        Retrieve the URL where this file can be downloaded.

        :return: The URL.
        """
        return 'https://i.4cdn.org/{0}/{1}.{2}'.format(self.board, self.id,
                                                       self.extension)

    def save_to(self, directory, name_fmt, verify=True):
        """
        Download and save this file.

        :param directory: The directory to save this file within.
        :param name_fmt: A function taking this instance and returning a file
                         name.
        :param verify: Whether to verify the file's checksum once it is written
                       (default: true).
        :raise IOError: If the file cannot be written, or its checksum does not
                        match the one reported by 4Chan.
        """

        # N.B. urllib doesn't handle unicode well - encode everything before
        #      handing over

        destination = os.path.join(directory, name_fmt(self))\
            .encode(sys.getfilesystemencoding())
        if os.path.isfile(destination):
            logger.info('%s already exists; skipping download', self)
        else:
            logger.info('Downloading %s', self)
            request.urlretrieve(self.url, destination)
        if verify and util.md5_file(destination) != self.md5:
            raise IOError('Verify failed: checksum mismatch'.format(self))

    @staticmethod
    def parse_json(board, json):
        """
        Create a file object from 4Chan's API format.

        :param board: The board this file was uploaded to.
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

        return File(json['tim'], board, json['filename'], json['ext'][1:],
                    json['fsize'], json['w'], json['h'],
                    unpack_hash(json['md5']).rstrip())

    def __str__(self):
        return 'File({0}, {1}.{2}, {3}, {4}x{5})'.format(
            self.id, self.name, self.extension, util.bytes_fmt(self.size),
            self.width, self.height)
