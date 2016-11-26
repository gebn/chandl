# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import TestCase
import copy

from chandl import util
from chandl.model.file import File


class TestFile(TestCase):

    _BOARD = 'wg'

    _POST_NO_FILE = {
        'no': 1978945,
        'now': '11/23/16(Wed)04:52:24',
        'name': 'Anonymous',
        'com': '<a href=\"#p1978196\" class=\"quotelink\">&gt;&gt;1978196</a>'
               '<br>This is some HTML.',
        'time': 1479894744,
        'resto': 1978004
    }

    _POST_VALID = {
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
    _POST_VALID_FILE_MD5 = '9af02b887481156059afac90e5cd7996'
    _POST_VALID_FILE_URL = 'https://i.4cdn.org/wg/1479891251942.jpg'

    @classmethod
    def setUpClass(cls):
        cls.file = File.parse_json(cls._BOARD, cls._POST_VALID)

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
        file = File.parse_json(self._BOARD, file_json)
        self.assertEqual(file.name, filename[:30])

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
