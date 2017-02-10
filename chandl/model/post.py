# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
import six
import pytz

from chandl import util
from chandl.model.file import File


@six.python_2_unicode_compatible
class Post:
    """
    Represents a 4Chan post.
    """

    def __init__(self, board, id_, timestamp, body=None, file_=None):
        """
        Initialise a new post instance.

        :param board: The board this post was submitted to.
        :param id_: The post number.
        :param timestamp: When this post was submitted.
        :param body: The body of this post, if one exists.
        :param file_: This post's file, if one exists.
        """
        self.board = board
        self.id = id_
        self.timestamp = timestamp
        self.body = body
        self.file = file_

    @property
    def has_file(self):
        """
        Find whether this post has a file.

        :return: True if it does, false otherwise.
        """
        return self.file is not None

    @staticmethod
    def parse_json(board, json):
        """
        Create a post instance from JSON returned by the 4Chan API.

        :param board: The board that was requested.
        :param json: The post's parsed JSON as a dictionary.
        :return: The created post instance.
        """
        file_ = File.parse_json(board, json) if 'tim' in json else None
        comment = util.unescape_html(json['com']) if 'com' in json else None
        return Post(board, json['no'],
                    datetime.utcfromtimestamp(
                        json['time']).replace(tzinfo=pytz.utc),
                    comment, file_)

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
               and other.__dict__ == self.__dict__

    def __str__(self):
        return 'Post({0}, {1}, {2})'.format(self.id,
                                            str(self.timestamp),
                                            self.file)
