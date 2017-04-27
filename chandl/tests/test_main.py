# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import argparse
import sys
import os
import contextlib
import six

from chandl import __main__ as main
from chandl.tests.model.test_thread import TestThread


@contextlib.contextmanager
def _suppress_stderr():
    save_stderr = sys.stderr
    try:
        sys.stderr = open(os.devnull, 'w')
        yield
    finally:
        sys.stderr.close()
        sys.stderr = save_stderr


class TestPrintError(unittest.TestCase):

    _MESSAGE = 'test message'

    def test_stream(self):
        try:
            sys.stderr = six.StringIO()
            main._print_error(self._MESSAGE)
            self.assertEquals(sys.stderr.getvalue(), self._MESSAGE + '\n')
        finally:
            sys.stderr = sys.__stderr__


class TestParseArgs(unittest.TestCase):

    _DUMMY_URL = 'https://boards.4chan.org/wg/thread/6851190'
    _BASE_ARGV = ['chandl', _DUMMY_URL]

    def test_version(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            main._parse_args(['-V'])

    def test_verbosity_implicit(self):
        self.assertEqual(main._parse_args(self._BASE_ARGV).verbosity, 0)

    def test_verbosity_count(self):
        self.assertEqual(main._parse_args(self._BASE_ARGV +
                                          ['-vvvv']).verbosity,
                         4)

    def test_filter_missing(self):
        self.assertListEqual(main._parse_args(self._BASE_ARGV).filter, [])

    def test_filter(self):
        self.assertEqual(
            main._parse_args(self._BASE_ARGV +
                             ['-f', 'abc,def', '-f', 'ghi']).filter,
            ['abc,def', 'ghi'])

    def test_exclude_missing(self):
        self.assertListEqual(main._parse_args(self._BASE_ARGV).exclude, [])

    def test_exclude(self):
        self.assertEqual(
            main._parse_args(self._BASE_ARGV +
                             ['-e', 'abc,def', '-e', 'ghi']).exclude,
            ['abc,def', 'ghi'])

    def test_output_dir_missing(self):
        self.assertEqual(main._parse_args(self._BASE_ARGV).output_dir,
                         os.getcwd())

    def test_output_dir_no_arg(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            main._parse_args(self._BASE_ARGV + ['-o'])

    def test_output_dir(self):
        self.assertEqual(
            main._parse_args(self._BASE_ARGV + ['-o', 'path']).output_dir,
            'path')

    def test_thread_dir_missing(self):
        self.assertIsNone(main._parse_args(self._BASE_ARGV).thread_dir)

    def test_thread_dir_no_arg(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            main._parse_args(self._BASE_ARGV + ['-t'])

    def test_thread_dir(self):
        self.assertEqual(
            main._parse_args(self._BASE_ARGV + ['-t', 'path']).thread_dir,
            'path')

    def test_name_missing(self):
        self.assertEqual(main._parse_args(self._BASE_ARGV).name,
                         '{file.id} - {file.name}.{file.extension}')

    def test_name_no_arg(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            main._parse_args(self._BASE_ARGV + ['-n'])

    def test_name(self):
        self.assertEqual(
            main._parse_args(self._BASE_ARGV + ['-n', 'namefmt']).name,
            'namefmt')

    def test_parallelism_missing(self):
        self.assertEqual(
            main._parse_args(self._BASE_ARGV).parallelism, 2)

    def test_parallelism_no_arg(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            main._parse_args(self._BASE_ARGV + ['-p'])

    def test_parallelism(self):
        self.assertEqual(
            main._parse_args(self._BASE_ARGV + ['-p', '4']).parallelism, 4)

    def test_url_missing(self):
        with self.assertRaises(SystemExit), _suppress_stderr():
            main._parse_args([])

    def test_url(self):
        self.assertEqual(
            main._parse_args(self._BASE_ARGV).url,
            self._DUMMY_URL)


class TestRemoveUnwanted(unittest.TestCase):

    _NO_ARGS = argparse.Namespace(filter=[], exclude=[])

    def test_no_posts_no_args(self):
        self.assertListEqual(main._remove_unwanted([], self._NO_ARGS),
                             [])

    def test_posts_no_args(self):
        self.assertListEqual(
            main._remove_unwanted(TestThread.POSTS, self._NO_ARGS),
            [post for post in TestThread.POSTS if post.has_file])

    def test_posts_filter_png(self):
        self.assertListEqual(
            main._remove_unwanted(TestThread.POSTS,
                                  argparse.Namespace(filter=['png'],
                                                     exclude=[])),
            [post for post in TestThread.POSTS
             if post.has_file and post.file.extension == 'png'])

    def test_posts_exclude_png(self):
        name = '1475710924523.jpg'
        self.assertListEqual(
            main._remove_unwanted(TestThread.POSTS,
                                  argparse.Namespace(filter=[],
                                                     exclude=[name])),
            [post for post in TestThread.POSTS
             if post.has_file and post.file.name != name])
