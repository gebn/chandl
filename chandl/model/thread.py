# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import re
import six
import requests

from chandl import util
from chandl.model.post import Post

logger = logging.getLogger(__name__)


@six.python_2_unicode_compatible
class Thread:
    """
    Represents a 4Chan thread.
    """

    def __init__(self, board, id_, subject, title, slug, posts):
        """
        Initialise a new thread instance.

        :param board: The board this thread exists within.
        :param id_: The post id of the first post in this thread.
        :param subject: The thread subject, if set.
        :param title: A name for the thread, resolved from the subject, comment,
                      or thread id.
        :param slug: The thread's URL fragment.
        :param posts: A list of posts in this thread.
        """
        self.board = board
        self.id = id_
        self.subject = subject
        self.title = title
        self.slug = slug
        self.posts = posts

    @property
    def url(self):
        """
        Generate a link where this thread can be viewed.

        :return: The URL.
        """
        return 'https://boards.4chan.org/{0}/thread/{1}/{2}'.format(
            self.board, self.id, self.slug)

    @staticmethod
    def _find_subject(post):
        """
        Identifies the most appropriate name for a thread.

        :param post: The first post's json.
        :return: A string containing the thread's resolved subject.
        """

        # if the post has a subject, it's easy
        if 'sub' in post:
            return util.unescape_html(post['sub'])

        # return the first sentence of the post content
        comment = util.unescape_html(post['com'])
        result = re.match(r'([^.:;?]+)', comment)
        if result:
            return result.group(1)

        # fall back to the post id
        return str(post['no'])

    @staticmethod
    def parse_json(board, json_):
        """
        Create a thread instance from JSON returned by the 4Chan API.

        :param board: The board that was requested.
        :param json_: The thread's parsed JSON as a dictionary.
        :return: The created thread instance.
        """
        if 'posts' not in json_ or not json_['posts']:
            raise ValueError('Thread does not contain any posts')

        first = json_['posts'][0]

        return Thread(board,
                      first['no'],
                      util.unescape_html(first['sub'])
                      if 'sub' in first else None,
                      Thread._find_subject(first),
                      first['semantic_url'],
                      [Post.parse_json(board, post)
                       for post in json_['posts']])

    @staticmethod
    def from_url(url, session=None):
        """
        Construct a thread instance from its URL.

        :param url: The URL of the thread to retrieve.
        :param session: The requests session to use to send the request.
        :return: The created thread instance.
        :raises IOError: If the thread could not be retrieved from 4chan.
        """
        # extract the board and thread ids
        result = re.search('boards\.4chan\.org/([a-z]+)/thread/([0-9]+)', url)
        if not result:
            raise ValueError('Invalid thread URL: {0}'.format(url))

        # construct a session if necessary
        if not session:
            session = util.create_session()

        # determine the URL
        api_url = 'https://a.4cdn.org/{0}/thread/{1}.json'.format(
            result.group(1), result.group(2))

        # download the JSON
        logger.debug('Retrieving JSON from %s', api_url)
        response = session.get(api_url)
        if response.status_code != requests.codes.ok:
            raise IOError('Request to 4chan failed with status code {0}'.format(
                response.status_code))
        try:
            return Thread.parse_json(result.group(1), response.json())
        except ValueError as e:
            raise IOError('Error parsing 4chan response: {0}'.format(e))

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
               and other.__dict__ == self.__dict__

    def __str__(self):
        return 'Thread({0}, {1})'.format(self.id, self.board)
