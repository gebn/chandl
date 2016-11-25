# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import multiprocessing
from functools import partial
from threading import Thread
from collections import deque


logger = logging.getLogger(__name__)


class Downloader:
    """
    A basic thread pool implementation to download multiple files
    simultaneously.
    """

    def __init__(self, directory, name_fmt, parallelism=4):
        """
        Initialise a new downloader instance. Instances can be reused.

        :param directory: The directory to save files in.
        :param name_fmt: A function taking a file instance and returning the
                         name to save it under.
        :param parallelism: The maximum number of threads to use to download
                            files per CPU. E.g. parallelism of 4 on a quad core
                            results in 20 threads.
        """

        self._directory = directory
        self._name_fmt = name_fmt
        self._threads = multiprocessing.cpu_count() * parallelism
        self._queue = deque()
        self._pool = []  # invariant: len(self._pool) <= self._threads

    @staticmethod
    def runner(self):
        """
        A single thread's execution.

        :param self: The downloader instance the thread belongs to.
        """

        while True:
            try:
                file_ = self._queue.popleft()
                Downloader.handle(self, file_)
            except IndexError:
                # no items left to process - let function return
                break

    @staticmethod
    def handle(self, file_):
        """
        Downloads a file.

        :param self: The downloader context.
        :param file_: The file to download.
        """

        try:
            file_.save_to(self._directory, self._name_fmt)
        except IOError as e:
            logger.exception('Failed to write %s: %s', file_, e.message)

    def _queue_all(self, files):
        """
        Add all files in an iterable to the download queue.

        :param files: The files to add.
        """

        for file_ in files:
            self._queue.append(file_)

    def download(self, files):
        """
        Download a set of files.

        :param files: An iterable containing the files to download. They will
                      be downloaded in order.
        """

        # populate the queue
        self._queue_all(files)

        # don't launch more threads than files
        threads = min(self._threads, len(self._queue))
        logger.debug('Will use %d threads for downloading', threads)

        # launch threads
        target = partial(Downloader.runner, self)
        for _ in range(threads):
            thread = Thread(target=target)
            thread.start()
            self._pool.append(thread)
        logger.debug('All threads launched')

        # wait for all threads to finish
        for i in range(threads):
            self._pool[i].join()
