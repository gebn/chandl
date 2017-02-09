# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import TestCase
from datetime import datetime

from chandl import util
from chandl.model.post import Post


class TestPost(TestCase):

    _BOARD = 'wg'

    _POST = {
        'no': 1978935,
        'now': '11/23/16(Wed)03:54:11',
        'name': 'Anonymous',
        'com': '<a href=\"#p1978934\" class=\"quotelink\">&gt;&gt;1978934</a>'
               '<br>4/?',
        'filename': '026 - 9pVmOxz',
        'ext': '.jpg',
        'w': 1000,
        'h': 1415,
        'tn_w': 88,
        'tn_h': 125,
        'tim': 1479891251942,
        'time': 1479891251,
        'md5': 'mvAriHSBFWBZr6yQ5c15lg==',
        'fsize': 787710,
        'resto': 1978004
    }

    _POST_NO_FILE = {
        'no': 1978945,
        'now': '11/23/16(Wed)04:52:24',
        'name': 'Anonymous',
        'com': '<a href=\"#p1978196\" class=\"quotelink\">&gt;&gt;1978196</a>'
               '<br>This is some HTML.',
        'time': 1479894744,
        'resto': 1978004
    }

    _POST_NO_BODY = {
        'no': 1978719,
        'now': '11/22/16(Tue)11:22:20',
        'name': 'Anonymous',
        'filename': '0guzMVA',
        'ext': '.jpg',
        'w': 1920,
        'h': 1200,
        'tn_w': 125,
        'tn_h': 78,
        'tim': 1479831740360,
        'time': 1479831740,
        'md5': 'cpoZmr+1xg58LzT2DIK2ZQ==',
        'fsize': 128012,
        'resto': 1978004
    }

    @classmethod
    def setUpClass(cls):
        cls.post = Post.parse_json(cls._BOARD, cls._POST)
        cls.post_no_body = Post.parse_json(cls._BOARD, cls._POST_NO_BODY)
        cls.post_no_file = Post.parse_json(cls._BOARD, cls._POST_NO_FILE)

    def test_board(self):
        self.assertEqual(self.post.board, self._BOARD)

    def test_id(self):
        self.assertEqual(self.post.id, self._POST['no'])

    def test_timestamp(self):
        self.assertEqual(self.post.timestamp,
                         datetime.utcfromtimestamp(self._POST['time']))

    def test_body(self):
        self.assertEqual(self.post.body, util.unescape_html(self._POST['com']))

    def test_no_body(self):
        self.assertIsNone(self.post_no_body.body)

    def test_file(self):
        self.assertEqual(self.post.id, self._POST['no'])

    def test_no_file(self):
        self.assertIsNone(self.post_no_file.file)

    def test_has_file_true(self):
        self.assertTrue(self.post.has_file)

    def test_has_file_false(self):
        self.assertFalse(self.post_no_file.has_file)

    def test_str(self):
        self.assertEqual(str(self.post),
                         'Post({0}, {1}, {2}, {3})'.format(
                             self._POST['no'],
                             str(datetime.utcfromtimestamp(self._POST['time'])),
                             util.unescape_html(self._POST['com']),
                             str(self.post.file)))
