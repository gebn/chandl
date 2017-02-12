# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import TestCase
import datetime
import pytz

from chandl import util
from chandl.model.file import File
from chandl.model.post import Post


class TestPost(TestCase):

    BOARD = 'wg'

    POST_JSON = {
        'no': 6849229,
        'now': '02/11/17(Sat)21:33:46',
        'name': 'Anonymous',
        'sub': 'Financial backgrounds',
        'com': '<a href=\"#p1978934\" class=\"quotelink\">&gt;&gt;1978934</a>'
               '<br>4/?',
        'filename': 'wall_2',
        'ext': '.jpg',
        'w': 1200,
        'h': 934,
        'tn_w': 250,
        'tn_h': 194,
        'tim': 1486866826992,
        'time': 1486866826,
        'md5': 'iKLZQLYdEGgYi/xuNnd9nQ==',
        'fsize': 270555,
        'resto': 1978004,
        'bumplimit': 0,
        'imagelimit': 0,
        'semantic_url': 'financial-backgrounds',
        'replies': 2,
        'images': 2,
        'unique_ips': 1
    }
    POST_JSON_FILE_MD5 = '88a2d940b61d1068188bfc6e36777d9d'
    POST_JSON_FILE_URL = 'https://i.4cdn.org/wg/1486866826992.jpg'

    POST = Post(BOARD, POST_JSON['no'],
                datetime.datetime(2017, 2, 12, 2, 33, 46, tzinfo=pytz.utc),
                '<a href=\"#p1978934\" class=\"quotelink\">>>1978934</a>'
                '<br>4/?', File.parse_json(BOARD, POST_JSON))

    _POST_NO_BODY_JSON = {
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

    _POST_NO_BODY = Post(BOARD, _POST_NO_BODY_JSON['no'],
                         datetime.datetime(2016, 11, 22, 16, 22, 20,
                                           tzinfo=pytz.utc),
                         file_=File.parse_json(BOARD, _POST_NO_BODY_JSON))

    POST_NO_FILE_JSON = {
        'no': 1978945,
        'now': '11/23/16(Wed)04:52:24',
        'name': 'Anonymous',
        'com': '<a href=\"#p1978196\" class=\"quotelink\">&gt;&gt;1978196</a>'
               '<br>This is some HTML.',
        'time': 1479894744,
        'resto': 1978004
    }

    _POST_NO_FILE = Post(BOARD, POST_NO_FILE_JSON['no'],
                         datetime.datetime(2016, 11, 23, 9, 52, 24,
                                           tzinfo=pytz.utc),
                         '<a href=\"#p1978196\" class=\"quotelink\">>>1978196</'
                         'a><br>This is some HTML.')

    def test_board(self):
        self.assertEqual(self.POST.board, self.BOARD)

    def test_id(self):
        self.assertEqual(self.POST.id, self.POST_JSON['no'])

    def test_timestamp(self):
        self.assertEqual(self.POST.timestamp,
                         datetime.datetime.utcfromtimestamp(
                             self.POST_JSON['time']).replace(tzinfo=pytz.utc))

    def test_body(self):
        self.assertEqual(self.POST.body,
                         util.unescape_html(self.POST_JSON['com']))

    def test_no_body(self):
        self.assertIsNone(self._POST_NO_BODY.body)

    def test_file(self):
        self.assertEqual(self.POST.id, self.POST_JSON['no'])

    def test_no_file(self):
        self.assertIsNone(self._POST_NO_FILE.file)

    def test_has_file_true(self):
        self.assertTrue(self.POST.has_file)

    def test_has_file_false(self):
        self.assertFalse(self._POST_NO_FILE.has_file)

    def test_parse_json(self):
        self.assertEqual(Post.parse_json(self.BOARD, self.POST_JSON),
                         self.POST)

    def test_str(self):
        self.assertEqual(
            str(self.POST),
            'Post({0}, {1}, {2})'.format(
                self.POST_JSON['no'],
                str(datetime.datetime.utcfromtimestamp(
                    self.POST_JSON['time']).replace(tzinfo=pytz.utc)),
                str(self.POST.file)))
