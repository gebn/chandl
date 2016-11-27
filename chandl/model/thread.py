# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import re
import six
import requests

from chandl.model.posts import Posts
from chandl.model.post import Post


logger = logging.getLogger(__name__)


@six.python_2_unicode_compatible
class Thread:
    """
    Represents a 4Chan thread.
    """

    def __init__(self, board, id_, subject, slug, posts):
        """
        Initialise a new thread instance.

        :param board: The board this thread exists within.
        :param id_: The post id of the first post in this thread.
        :param subject: The thread subject, if set.
        :param slug: The thread's URL fragment.
        :param posts: Posts within this thread.
        """
        self.board = board
        self.id = id_
        self.subject = subject
        self.slug = slug
        self.posts = posts

    @property
    def url(self, secure=True):
        """
        Generate a link where this thread can be viewed.

        :param secure: Whether or not to generate an HTTPS link.
                       Defaults to true.
        :return: The URL.
        """
        protocol = 'https' if secure else 'http'
        return '{0}://boards.4chan.org/{1}/thread/{2}/{3}'.format(
            protocol, self.board, self.id, self.slug)

    @staticmethod
    def parse_json(board, json_):
        """
        Create a thread instance from JSON returned by the 4Chan API.

        :param board: The board that was requested.
        :param json_: The thread's parsed JSON as a dictionary.
        :return: The created thread instance.
        """
        if not json_['posts']:
            raise ValueError('A thread must contain at least one post')

        first = json_['posts'][0]

        return Thread(board,
                      first['no'],
                      first['sub'] if 'sub' in first else None,
                      first['semantic_url'],
                      Posts([Post.parse_json(board, post)
                             for post in json_['posts']]))

    @staticmethod
    def from_url(url, secure=True):
        """
        Construct a thread instance from its URL.

        :param url: The URL of the thread to retrieve.
        :param secure: Whether or not to retrieve the board using a secure
                       connection.
        :return: The created thread instance.
        :raises IOError: If the thread could not be retrieved from 4chan.
        """
        # extract the board and thread ids
        result = re.search('boards\.4chan\.org/([a-z]+)/thread/([0-9]+)', url)
        if not result:
            raise ValueError('Invalid thread URL: {0}'.format(url))

        # download the JSON
        protocol = 'https' if secure else 'http'
        api_url = '{0}://a.4cdn.org/{1}/thread/{2}.json'.format(
            protocol, result.group(1), result.group(2))
        logger.debug('Retrieving JSON from %s', api_url)
        response = requests.get(api_url)
        if response.status_code != requests.codes.ok:
            raise IOError('Request to 4chan failed with status code {0}'.format(
                response.status_code))
        return Thread.parse_json(result.group(1), response.json())

    def __str__(self):
        return 'Thread({0}, {1})'.format(self.id, self.board)
