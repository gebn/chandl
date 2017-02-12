# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import os
from httmock import all_requests, response, HTTMock
from pyfakefs import fake_filesystem_unittest

from chandl import util
from chandl.model import file
from chandl.model.file import File

from chandl.tests.model.test_post import TestPost

_REAL_OPEN = open


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


class TestFile(fake_filesystem_unittest.TestCase):

    _RESOURCES_DIR = os.path.join(os.path.dirname(__file__), 'resources')

    @classmethod
    def setUpClass(cls):
        cls.file = File(TestPost.POST_JSON['tim'], TestPost.BOARD,
                        TestPost.POST_JSON['filename'],
                        TestPost.POST_JSON['ext'][1:],
                        TestPost.POST_JSON['fsize'], TestPost.POST_JSON['w'],
                        TestPost.POST_JSON['h'], TestPost.POST_JSON_FILE_MD5)

    def setUp(self):
        self.setUpPyfakefs()

    def test_id(self):
        self.assertEqual(self.file.id, TestPost.POST_JSON['tim'])

    def test_board(self):
        self.assertEqual(self.file.board, TestPost.BOARD)

    def test_name(self):
        self.assertEqual(self.file.name, TestPost.POST_JSON['filename'])

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

    def test_save_to_exists(self):
        # to ensure it's not re-downloading, make any re-download fail by not
        # configuring HTTMock

        directory = '/tmp'
        name = 'dl.jpg'
        path = os.path.join(directory, name)

        # copy real file to fakefs
        with _REAL_OPEN(
                os.path.join(self._RESOURCES_DIR,
                             TestPost.POST.file.filename), 'rb') as real_file:
            self.fs.CreateFile(path, contents=real_file.read())

        self.file.save_to(directory, name)

    def test_save_to_exists_md5_mismatch(self):
        # noinspection PyUnusedLocal
        @all_requests
        def response_content(url, request):
            with _REAL_OPEN(os.path.join(
                    self._RESOURCES_DIR,
                    TestPost.POST.file.filename), 'rb') as f:
                return response(content=f.read(), stream=True)

        directory = '/tmp'
        name = 'corrupt.jpg'
        path = os.path.join(directory, name)

        self.fs.CreateFile(path, contents='corrupt content')
        with HTTMock(response_content):
            self.file.save_to(directory, name)
        self.assertEqual(util.md5_file(path), TestPost.POST.file.md5)

    def test_save_to_non_200(self):
        # noinspection PyUnusedLocal
        @all_requests
        def response_content(url, request):
            return response(404)

        with HTTMock(response_content), self.assertRaises(IOError):
            self.file.save_to(self._RESOURCES_DIR, self.file.filename)

    def test_save_to_verify_mismatch(self):
        # noinspection PyUnusedLocal
        @all_requests
        def response_content(url, request):
            return response(content='corrupt content', stream=True)

        with HTTMock(response_content), self.assertRaises(IOError):
            self.fs.CreateDirectory(self._RESOURCES_DIR)
            self.file.save_to(self._RESOURCES_DIR, 'dl.jpg')

    def test_save_to_ok(self):
        # noinspection PyUnusedLocal
        @all_requests
        def response_content(url, request):
            with _REAL_OPEN(os.path.join(
                    self._RESOURCES_DIR,
                    TestPost.POST.file.filename), 'rb') as f:
                return response(content=f.read(), stream=True)

        with HTTMock(response_content):
            self.fs.CreateDirectory(self._RESOURCES_DIR)
            self.file.save_to(self._RESOURCES_DIR, 'dl.jpg')

        self.assertEqual(
            util.md5_file(os.path.join(self._RESOURCES_DIR,
                                       'dl.jpg')),
            TestPost.POST.file.md5)

    def test_str(self):
        self.assertEqual(str(self.file),
                         'File({0}, {1}.{2}, {3}, {4}x{5})'.format(
                             TestPost.POST_JSON['tim'],
                             TestPost.POST_JSON['filename'],
                             TestPost.POST_JSON['ext'][1:],
                             util.bytes_fmt(TestPost.POST_JSON['fsize']),
                             TestPost.POST_JSON['w'],
                             TestPost.POST_JSON['h']))
