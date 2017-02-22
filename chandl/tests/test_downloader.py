# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import mock
import os
import signal

from chandl import downloader


class TestHandleSigint(unittest.TestCase):

    def setUp(self):
        downloader._interrupted = False

    def tearDown(self):
        downloader._interrupted = False

    def test_interrupted(self):
        downloader._handle_sigint(None, None)
        self.assertTrue(downloader._interrupted)


class TestRedirectSigint(unittest.TestCase):

    def setUp(self):
        downloader._interrupted = False

    def tearDown(self):
        downloader._interrupted = False

    def test_interrupted(self):
        handler = mock.MagicMock()
        with downloader._redirect_sigint(handler):
            os.kill(os.getpid(), signal.SIGINT)
        handler.assert_called_once()
