# -*- coding: utf-8 -*-
from unittest import TestCase
import sys
import os
import logging

from chandl import util


class TestBytesFmt(TestCase):

    _TRIALS = {
        32242: '31.5 KiB',
        0: '0.0 B',
        -1: '1.0 B',
        1024: '1.0 KiB',
        1024 * 1024: '1.0 MiB'
    }

    def test_none(self):
        with self.assertRaises(ValueError):
            util.bytes_fmt(None)

    def test_trials(self):
        for number, formatted in self._TRIALS.items():
            self.assertEqual(util.bytes_fmt(number), formatted)


class TestDecodeCliArg(TestCase):

    def test_empty(self):
        with self.assertRaises(ValueError):
            util.decode_cli_arg(None)

    def test_valid(self):
        arg = u'test_arg_value'
        self.assertEqual(
            util.decode_cli_arg(arg.encode(sys.getfilesystemencoding())), arg)


class TestMakeFilename(TestCase):

    _NO_CHANGE = ['file_name.jpg',
                  'File name2.png',
                  '124_nAme22.png.abc']

    _MODIFIED = {
        'my%file"name().png': 'myfilename.png',
        '$*$*.webm': '.webm'
    }

    _UNICODE = {
        'Sîne klâwen durh': 'Sine klawen durh',
        'Τη γλώσσα μου έδωσαν': 'Te glossa mou edosan',
        'ღმერთსი შემვედრე': 'gmertsi shemvedre'
    }

    def test_none(self):
        with self.assertRaises(ValueError):
            util.make_filename(None)

    def test_empty(self):
        with self.assertRaises(ValueError):
            print(util.make_filename('$$$'))

    def test_no_change(self):
        for name in self._NO_CHANGE:
            self.assertEqual(util.make_filename(name), name)

    def test_modified(self):
        for original, mutated in self._MODIFIED.items():
            self.assertEqual(util.make_filename(original), mutated)

    def test_unicode(self):
        for original, mutated in self._UNICODE.items():
            self.assertEqual(util.make_filename(original), mutated)


class TestMd5File(TestCase):

    _TESTS_DIRECTORY = os.path.join(os.path.dirname(__file__), 'md5_tests')

    def test_none(self):
        with self.assertRaises(ValueError):
            util.md5_file(None)

    def test_not_file(self):
        with self.assertRaises(FileNotFoundError):
            util.md5_file('does_not_exist')

    def test_valid_hashes(self):
        for filename in os.listdir(self._TESTS_DIRECTORY):
            path = os.path.join(self._TESTS_DIRECTORY, filename)
            self.assertEqual(util.md5_file(path), os.path.basename(path))


class TestLogLevelFromVerbosity(TestCase):

    def test_warning(self):
        self.assertEqual(util.log_level_from_vebosity(0), logging.WARNING)

    def test_info(self):
        self.assertEqual(util.log_level_from_vebosity(1), logging.INFO)

    def test_debug(self):
        self.assertEqual(util.log_level_from_vebosity(2), logging.DEBUG)
        self.assertEqual(util.log_level_from_vebosity(None), logging.DEBUG)
