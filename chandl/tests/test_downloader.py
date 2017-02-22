# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import unittest
import os
import signal

from chandl import downloader
from chandl.tests.model.test_thread import TestThread


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
        with downloader._redirect_sigint():
            os.kill(os.getpid(), signal.SIGINT)
        self.assertTrue(downloader._interrupted)


class TestDownloadResult(unittest.TestCase):

    _COMPLETED_JOBS = [post for post in TestThread.POSTS
                       if post.has_file and post.file.extension == 'jpg']
    _REMAINING_JOBS = [post for post in TestThread.POSTS
                       if post.has_file and post.file.extension == 'png']
    _ELAPSED = datetime.timedelta(microseconds=98520934)

    @classmethod
    def setUpClass(cls):
        cls.result = downloader.DownloadResult(cls._COMPLETED_JOBS,
                                               cls._REMAINING_JOBS,
                                               cls._ELAPSED)

    def test_posts_size(self):
        self.assertEqual(
            downloader.DownloadResult._posts_size(self._COMPLETED_JOBS),
            sum([post.file.size for post in self._COMPLETED_JOBS]))

    def test_str(self):
        self.assertEqual(str(self.result),
                         '2/3 jobs completed, 1 remaining\n'
                         '646.2 KiB/681.0 KiB downloaded, 34.8 KiB remaining\n'
                         'Duration: 98.521 seconds (6.6 KiB/s)')
