# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import copy

from chandl import util
from chandl.model import file
from chandl.model.file import File


class TestExpandFilters(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(file.expand_filters([]), set())

    def test_duplicates(self):
        self.assertEqual(file.expand_filters(['webm', 'jpg', 'webm']),
                         {'webm', 'jpg'})

    def test_expand_type(self):
        self.assertEqual(file.expand_filters(file._FILTERS['videos']),
                         set(file.TYPE_VIDEO))

    def test_csv(self):
        self.assertEqual(file.expand_filters(['webm,jpg,webm', 'png,jpg']),
                         {'webm', 'jpg', 'png'})

    def test_strip(self):
        self.assertEqual(file.expand_filters(['webm  ', ' jpg', '   webm']),
                         {'webm', 'jpg'})

    def test_mixed(self):
        self.assertEqual(file.expand_filters(['webm , gif ', ' jpg,png',
                                              '   gif,webm,videos']),
                         set(['webm', 'gif', 'jpg', 'png'] + file.TYPE_VIDEO))


class TestFile(unittest.TestCase):

    _POST_NO_FILE = {
        'no': 1978945,
        'now': '11/23/16(Wed)04:52:24',
        'name': 'Anonymous',
        'com': '<a href=\"#p1978196\" class=\"quotelink\">&gt;&gt;1978196</a>'
               '<br>This is some HTML.',
        'time': 1479894744,
        'resto': 1978004
    }

    _BOARD = 'wg'
    _ID = 6840627

    _POST_VALID = {
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
    }

    _POST_VALID_FILE_MD5 = 'e7aca2209260ce786aba97f7baedb1b8'
    _POST_VALID_FILE_URL = 'https://i.4cdn.org/wg/1486016715106.jpg'

    @classmethod
    def setUpClass(cls):
        cls.file = File(cls._POST_VALID['tim'], cls._BOARD,
                        cls._POST_VALID['filename'], cls._POST_VALID['ext'][1:],
                        cls._POST_VALID['fsize'], cls._POST_VALID['w'],
                        cls._POST_VALID['h'], cls._POST_VALID_FILE_MD5)

    def test_id(self):
        self.assertEqual(self.file.id, self._POST_VALID['tim'])

    def test_board(self):
        self.assertEqual(self.file.board, self._BOARD)

    def test_name(self):
        self.assertEqual(self.file.name, self._POST_VALID['filename'])

    def test_long_name(self):
        filename = 'long' * 10
        file_json = copy.copy(self._POST_VALID)
        file_json['filename'] = filename
        file_ = File.parse_json(self._BOARD, file_json)
        self.assertEqual(file_.name, filename[:30])

    def test_extension(self):
        self.assertEqual(self.file.extension, self._POST_VALID['ext'][1:])

    def test_size(self):
        self.assertEqual(self.file.size, self._POST_VALID['fsize'])

    def test_width(self):
        self.assertEqual(self.file.width, self._POST_VALID['w'])

    def test_height(self):
        self.assertEqual(self.file.height, self._POST_VALID['h'])

    def test_md5(self):
        self.assertEqual(self.file.md5, self._POST_VALID_FILE_MD5)

    def test_parse_json_no_file(self):
        with self.assertRaises(ValueError):
            File.parse_json(self._BOARD, self._POST_NO_FILE)

    def test_parse_json_file(self):
        self.assertEqual(File.parse_json(self._BOARD, self._POST_VALID),
                         self.file)

    def test_url(self):
        self.assertEqual(self.file.url, self._POST_VALID_FILE_URL)

    def test_str(self):
        self.assertEqual(str(self.file),
                         'File({0}, {1}.{2}, {3}, {4}x{5})'.format(
                             self._POST_VALID['tim'],
                             self._POST_VALID['filename'],
                             self._POST_VALID['ext'][1:],
                             util.bytes_fmt(self._POST_VALID['fsize']),
                             self._POST_VALID['w'],
                             self._POST_VALID['h']))
