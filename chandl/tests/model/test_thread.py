# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import datetime
import json
import pytz
from httmock import all_requests, response, HTTMock

from chandl.model.file import File
from chandl.model.post import Post
from chandl.model.thread import Thread


class TestThread(unittest.TestCase):

    _THREAD_JSON = {
        'posts': [
            {
                'bumplimit': 0,
                'com': 'No more, no less',
                'ext': '.jpg',
                'filename': 'IMG_5433',
                'fsize': 35649,
                'h': 768,
                'imagelimit': 0,
                'images': 12,
                'md5': '56yiIJJgznhqupf3uu2xuA==',
                'name': 'Anonymous',
                'no': 6840627,
                'now': '02/02/17(Thu)01:25:15',
                'replies': 20,
                'resto': 0,
                'semantic_url': 'monty-python-papes',
                'sub': 'Monty Python Papes',
                'tim': 1486016715106,
                'time': 1486016715,
                'tn_h': 140,
                'tn_w': 250,
                'unique_ips': 18,
                'w': 1366
            },
            {
                'com': 'I love that... wish there WERE more monty python papes',
                'name': 'Anonymous',
                'no': 6841819,
                'now': '02/03/17(Fri)03:43:48',
                'resto': 6840627,
                'time': 1486111428
            },
            {
                'ext': '.jpg',
                'filename': 'stretched-32086',
                'fsize': 587095,
                'h': 1080,
                'md5': '3tdY3WI0UqMC+Ia+fLuyug==',
                'name': 'Anonymous',
                'no': 6842016,
                'now': '02/03/17(Fri)09:53:15',
                'resto': 6840627,
                'tim': 1486133595824,
                'time': 1486133595,
                'tn_h': 70,
                'tn_w': 125,
                'w': 1920
            },
            {
                'com': '<a href="#p6840627" class="quotelink">&gt;&gt;6840627</'
                       'a><br>All I have. Thanks for the sparrow one!',
                'ext': '.jpg',
                'filename': '1475710924523',
                'fsize': 74606,
                'h': 1080,
                'md5': 'DcWYVYrdxLwagDoS6D4e/w==',
                'name': 'Anonymous',
                'no': 6842026,
                'now': '02/03/17(Fri)10:06:10',
                'resto': 6840627,
                'tim': 1486134370795,
                'time': 1486134370,
                'tn_h': 70,
                'tn_w': 125,
                'w': 1920
            }
        ]
    }
    _BOARD = 'wg'
    _ID = 6840627
    _SUBJECT = 'Monty Python Papes'
    _TITLE = _SUBJECT
    _SLUG = 'monty-python-papes'
    _POSTS = [
        Post(_BOARD, 6840627,
             datetime.datetime(2017, 2, 2, 6, 25, 15, tzinfo=pytz.utc),
             'No more, no less',
             File(1486016715106, _BOARD, 'IMG_5433', 'jpg', 35649, 1366,
                  768, 'e7aca2209260ce786aba97f7baedb1b8')),
        Post(_BOARD, 6841819,
             datetime.datetime(2017, 2, 3, 8, 43, 48, tzinfo=pytz.utc),
             'I love that... wish there WERE more monty python papes'),
        Post(_BOARD, 6842016,
             datetime.datetime(2017, 2, 3, 14, 53, 15, tzinfo=pytz.utc),
             file_=File(1486133595824, _BOARD, 'stretched-32086', 'jpg', 587095,
                        1920, 1080, 'ded758dd623452a302f886be7cbbb2ba')),
        Post(_BOARD, 6842026,
             datetime.datetime(2017, 2, 3, 15, 6, 10, tzinfo=pytz.utc),
             '<a href="#p6840627" class="quotelink">>>6840627</a><br>All I have'
             '. Thanks for the sparrow one!',
             File(1486134370795, _BOARD, '1475710924523', 'jpg', 74606, 1920,
                  1080, '0dc598558addc4bc1a803a12e83e1eff'))
    ]

    _VALID_URL = 'http://boards.4chan.org/wg/thread/6847183'

    @classmethod
    def setUpClass(cls):
        cls._thread = Thread(cls._BOARD, cls._ID, cls._SUBJECT, cls._TITLE,
                             cls._SLUG, cls._POSTS)

    def test_url(self):
        self.assertEqual(
            self._thread.url,
            'https://boards.4chan.org/{0}/thread/{1}/{2}'.format(self._BOARD,
                                                                 self._ID,
                                                                 self._SLUG))

    def test_find_subject_subject_raw(self):
        self.assertEqual(
            Thread._find_subject({
                'sub': 'Monty Python Papes'
            }),
            'Monty Python Papes')

    def test_find_subject_subject_escaped(self):
        self.assertEqual(
            Thread._find_subject({
                'sub': '&gt;&gt; abcd &copy;&#163;'
            }),
            '>> abcd ©£')

    def test_find_subject_comment_single_sentence(self):
        self.assertEqual(
            Thread._find_subject({
                'com': 'this is the first - sentence.'
            }),
            'this is the first - sentence')

    def test_find_subject_comment_multiple_sentence(self):
        self.assertEqual(
            Thread._find_subject({
                'com': 'this is the first - sentence. here\'s another'
            }),
            'this is the first - sentence')

    def test_find_subject_fallback(self):
        self.assertEqual(
            Thread._find_subject({
                'no': 6840627,
                'com': '... abcd efgh'
            }),
            '6840627')

    def test_parse_json(self):
        self.assertEqual(Thread.parse_json(self._BOARD, self._THREAD_JSON),
                         self._thread)

    def test_parse_json_no_posts(self):
        with self.assertRaises(ValueError):
            Thread.parse_json(self._BOARD, {'posts': []})

    def test_from_url_invalid_url(self):
        with self.assertRaises(ValueError):
            Thread.from_url('http://boards.4chan.org/thread/abcd')

    def test_from_url_404(self):
        # noinspection PyUnusedLocal
        @all_requests
        def response_content(url, request):
            return response(404)

        with HTTMock(response_content), self.assertRaises(IOError):
            Thread.from_url(self._VALID_URL)

    def test_from_url_503(self):
        # noinspection PyUnusedLocal
        @all_requests
        def response_content(url, request):
            return response(403)

        with HTTMock(response_content), self.assertRaises(IOError):
            Thread.from_url(self._VALID_URL)

    def test_from_url_invalid_json(self):
        # noinspection PyUnusedLocal
        @all_requests
        def response_content(url, request):
            return response(content='invalid json here')

        with HTTMock(response_content), self.assertRaises(IOError):
            Thread.from_url(self._VALID_URL)

    def test_from_url_malformed_response(self):
        # noinspection PyUnusedLocal
        @all_requests
        def response_content(url, request):
            return response(content='{}')

        with HTTMock(response_content), self.assertRaises(IOError):
            Thread.from_url(self._VALID_URL)

    def test_from_url(self):
        # noinspection PyUnusedLocal
        @all_requests
        def response_content(url, request):
            return response(content=json.dumps(self._THREAD_JSON))

        with HTTMock(response_content):
            self.assertEqual(Thread.from_url(self._VALID_URL),
                             self._thread)

    def test_str(self):
        self.assertEqual(str(self._thread),
                         'Thread({0}, {1})'.format(self._ID, self._BOARD))
