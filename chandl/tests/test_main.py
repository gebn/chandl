# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import sys
import six

from chandl import __main__ as main


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

    def test_verbosity_missing(self):
        self.assertEqual(main._parse_args([self._DUMMY_URL]).verbosity, 0)

    def test_verbosity_count(self):
        self.assertEqual(main._parse_args([self._DUMMY_URL, '-vvvv']).verbosity,
                         4)
