# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import sys
import os
import six
import logging

import chandl
from chandl import util


class TestBytesFmt(unittest.TestCase):

    _TRIALS = {
        32242: '31.5 KiB',
        0: '0.0 B',
        -1: '1.0 B',
        1024: '1.0 KiB',
        1024 * 1024: '1.0 MiB',
        1024 * 2 ** 70: '1.0 YiB'
    }

    def test_none(self):
        with self.assertRaises(ValueError):
            util.bytes_fmt(None)

    def test_trials(self):
        for number, formatted in six.iteritems(self._TRIALS):
            self.assertEqual(util.bytes_fmt(number), formatted)


class TestDecodeCliArg(unittest.TestCase):

    _ARG_VALUE = 'test_arg_value'

    def test_empty(self):
        with self.assertRaises(ValueError):
            util.decode_cli_arg(None)

    @unittest.skipUnless(sys.version_info.major == 2,
                         'Only applies to Python 2')
    def test_valid_2(self):
        self.assertEqual(
            util.decode_cli_arg(
                self._ARG_VALUE.encode(sys.getfilesystemencoding())),
            self._ARG_VALUE)

    @unittest.skipUnless(sys.version_info.major == 3,
                         'Only applies to Python 3')
    def test_valid_3(self):
        self.assertEqual(util.decode_cli_arg(self._ARG_VALUE), self._ARG_VALUE)


class TestExpandCliArgs(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(util.expand_cli_args([]),
                         set())

    def test_strip(self):
        self.assertEqual(util.expand_cli_args(['  abc,  def ']),
                         {'abc', 'def'})

    def test_csv(self):
        self.assertEqual(util.expand_cli_args(['ghi,jkl , klm']),
                         {'ghi', 'jkl', 'klm'})

    def test_mixed(self):
        self.assertEqual(util.expand_cli_args(['nop', 'qrs,tuv']),
                         {'nop', 'qrs', 'tuv'})

    def test_duplicates(self):
        self.assertEqual(util.expand_cli_args(['wxyz', 'wxyz,wxyz']),
                         {'wxyz'})


class TestMakeFilename(unittest.TestCase):

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
        'ღმერთსი შემვედრე': 'g\'mertsi shemvedre'
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
        for original, mutated in six.iteritems(self._MODIFIED):
            self.assertEqual(util.make_filename(original), mutated)

    def test_unicode(self):
        for original, mutated in six.iteritems(self._UNICODE):
            self.assertEqual(util.make_filename(original), mutated)


class TestMd5File(unittest.TestCase):

    _TESTS_DIRECTORY = os.path.join(os.path.dirname(__file__), 'md5_tests')

    def test_none(self):
        with self.assertRaises(ValueError):
            util.md5_file(None)

    def test_not_file(self):
        with self.assertRaises(IOError):  # no FileNotFoundError in 2.7
            util.md5_file('does_not_exist')

    def test_valid_hashes(self):
        for filename in os.listdir(self._TESTS_DIRECTORY):
            path = os.path.join(self._TESTS_DIRECTORY, filename)
            self.assertEqual(util.md5_file(path), os.path.basename(path))


class TestLogLevelFromVerbosity(unittest.TestCase):

    def test_warning(self):
        self.assertEqual(util.log_level_from_vebosity(0), logging.WARNING)

    def test_info(self):
        self.assertEqual(util.log_level_from_vebosity(1), logging.INFO)

    def test_debug(self):
        self.assertEqual(util.log_level_from_vebosity(2), logging.DEBUG)
        self.assertEqual(util.log_level_from_vebosity(None), logging.DEBUG)


class TestCreateSession(unittest.TestCase):

    def test_user_agent(self):
        session = util.create_session()
        self.assertIn('User-Agent', session.headers)
        self.assertEqual(session.headers['User-Agent'],
                         'chandl/' + chandl.__version__)


class TestUnescapeHtml(unittest.TestCase):

    def test_all_encoded(self):
        self.assertEqual(
            util.unescape_html('&#x46;&#x6F;&#x6F;&#x20;&#xA9;&#x20;&#x62;&#x61'
                               ';&#x72;&#x20;&#x1D306;&#x20;&#x62;&#x61;&#x7A;&'
                               '#x20;&#x2603;&#x20;&#x71;&#x75;&#x78;'),
            'Foo © bar 𝌆 baz ☃ qux')

    def test_exotic_characters(self):
        self.assertEqual(
            util.unescape_html('Foo &#xA9; bar &#x1D306; baz &#x2603; qux'),
            'Foo © bar 𝌆 baz ☃ qux')

    def test_named_reference(self):
        self.assertEqual(util.unescape_html('&copy;'), '©')
