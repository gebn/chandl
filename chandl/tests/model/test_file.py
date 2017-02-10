# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import copy

from chandl import util
from chandl.model import file
from chandl.model.file import File

from chandl.tests.model.test_post import TestPost


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

    @classmethod
    def setUpClass(cls):
        cls.file = File(TestPost.POST_JSON['tim'], TestPost.BOARD,
                        TestPost.POST_JSON['filename'],
                        TestPost.POST_JSON['ext'][1:],
                        TestPost.POST_JSON['fsize'], TestPost.POST_JSON['w'],
                        TestPost.POST_JSON['h'], TestPost.POST_JSON_FILE_MD5)

    def test_id(self):
        self.assertEqual(self.file.id, TestPost.POST_JSON['tim'])

    def test_board(self):
        self.assertEqual(self.file.board, TestPost.BOARD)

    def test_name(self):
        self.assertEqual(self.file.name, TestPost.POST_JSON['filename'])

    def test_long_name(self):
        filename = 'long' * 10
        file_json = copy.copy(TestPost.POST_JSON)
        file_json['filename'] = filename
        file_ = File.parse_json(TestPost.BOARD, file_json)
        self.assertEqual(file_.name, filename[:30])

    def test_extension(self):
        self.assertEqual(self.file.extension, TestPost.POST_JSON['ext'][1:])

    def test_size(self):
        self.assertEqual(self.file.size, TestPost.POST_JSON['fsize'])

    def test_width(self):
        self.assertEqual(self.file.width, TestPost.POST_JSON['w'])

    def test_height(self):
        self.assertEqual(self.file.height, TestPost.POST_JSON['h'])

    def test_md5(self):
        self.assertEqual(self.file.md5, TestPost.POST_JSON_FILE_MD5)

    def test_parse_json_no_file(self):
        with self.assertRaises(ValueError):
            File.parse_json(TestPost.BOARD, TestPost.POST_NO_FILE_JSON)

    def test_parse_json_file(self):
        self.assertEqual(File.parse_json(TestPost.BOARD, TestPost.POST_JSON),
                         self.file)

    def test_url(self):
        self.assertEqual(self.file.url, TestPost.POST_JSON_FILE_URL)

    def test_str(self):
        self.assertEqual(str(self.file),
                         'File({0}, {1}.{2}, {3}, {4}x{5})'.format(
                             TestPost.POST_JSON['tim'],
                             TestPost.POST_JSON['filename'],
                             TestPost.POST_JSON['ext'][1:],
                             util.bytes_fmt(TestPost.POST_JSON['fsize']),
                             TestPost.POST_JSON['w'],
                             TestPost.POST_JSON['h']))
