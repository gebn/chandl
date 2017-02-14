# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import sys
import six

from chandl import __main__


class TestPrintError(unittest.TestCase):

    _MESSAGE = 'test message'

    def test_stream(self):
        try:
            sys.stderr = six.StringIO()
            __main__._print_error(self._MESSAGE)
            self.assertEquals(sys.stderr.getvalue(), self._MESSAGE + '\n')
        finally:
            sys.stderr = sys.__stderr__
