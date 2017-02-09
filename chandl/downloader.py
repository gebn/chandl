# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import multiprocessing
import time
import signal
import functools
import threading
import collections
import contextlib
import six
import datetime
import os
import requests
from progress.bar import Bar

from chandl import util


logger = logging.getLogger(__name__)

_interrupted = False


# noinspection PyUnusedLocal
def _handle_sigint(number, frame):
    """
    Called when we receive a SIGINT.

    :param number: The signal number (2 in this case).
    :param frame: The stack frame.
    """
    global _interrupted
    _interrupted = True


@contextlib.contextmanager
def _redirect_sigint():
    """
    For the duration of this function, a SIGINT will call _handle_sigint()
    rather than the normal Python routine.
    """
    original_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, _handle_sigint)
    try:
        yield
    except:
        raise
    finally:
        signal.signal(signal.SIGINT, original_handler)


@six.python_2_unicode_compatible
class DownloadResult:
    """
    Represents the outcome of a thread download.
    """

    @staticmethod
    def _posts_size(posts):
        """
        Find the total size of the files in all posts in a list.

        :param posts: The posts whose files to count.
        :return: The total size of the files in the posts in bytes.
        """
        return sum([post_.file.size for post_ in posts if post_.has_file])

    def __init__(self, completed_jobs, remaining_jobs, elapsed):
        """
        Initialise a new download result.

        :param completed_jobs: A list of posts that downloaded successfully.
        :param remaining_jobs: A list of posts that were not downloaded.
        :param elapsed: A timedelta representing the duration of the download.
        """
        self.downloaded_bytes = self._posts_size(completed_jobs)
        self.remaining_bytes = self._posts_size(remaining_jobs)
        self.total_bytes = self.downloaded_bytes + self.remaining_bytes

        self.completed_job_count = len(completed_jobs)
        self.remaining_job_count = len(remaining_jobs)
        self.total_jobs = self.completed_job_count + self.remaining_job_count

        self.completed_jobs = completed_jobs
        self.remaining_jobs = remaining_jobs
        self.elapsed = elapsed

    def __str__(self):
        """
        Get a formatted representation of this download's outcome.

        :return: The download statistics as a human-readable string.
        """
        string = '{0}/{1} jobs completed, {2} remaining{3}'.format(
            self.completed_job_count,
            self.total_jobs,
            self.remaining_job_count,
            os.linesep)
        string += '{0}/{1} downloaded, {2} remaining{3}'.format(
            util.bytes_fmt(self.downloaded_bytes),
            util.bytes_fmt(self.total_bytes),
            util.bytes_fmt(self.remaining_bytes),
            os.linesep)
        string += 'Duration: {0:0.3f} seconds ({1}/s)'.format(
            self.elapsed.total_seconds(),
            util.bytes_fmt(int(self.downloaded_bytes //
                               self.elapsed.total_seconds())))
        return string


class Downloader:
    """
    A basic thread pool implementation to download multiple files
    simultaneously.
    """

    def __init__(self, directory, name_fmt, parallelism=4):
        """
        Initialise a new downloader instance. Instances should not be reused.

        :param directory: The directory to save files in.
        :param name_fmt: A format specifier for file names.
        :param parallelism: The maximum number of threads to use to download
                            files per CPU. E.g. parallelism of 4 on a quad core
                            results in 16 threads.
        """
        self._directory = directory
        self._name_fmt = name_fmt
        self._threads = multiprocessing.cpu_count() * parallelism
        self._queue = collections.deque()

        self._lock = threading.Lock()

        self._completed_jobs = []

    @staticmethod
    def runner(self):
        """
        A single thread's execution.

        :param self: The downloader instance the thread belongs to.
        """
        session = requests.Session()
        while not _interrupted:
            try:
                post_ = self._queue.popleft()
                Downloader.handle(self, post_, session)
            except IndexError:
                # no items left to process - let function return
                break

    @staticmethod
    def handle(self, post_, session):
        """
        Downloads the file in a post.

        :param self: The downloader context.
        :param post_: The post to download.
        :param session: The requests session to use for the download.
        """
        try:
            name = self._name_fmt.format(**post_.__dict__)
            post_.file.save_to(self._directory, name, session=session)
            with self._lock:
                self._completed_jobs.append(post_)
        except IOError as e:
            logger.exception('Failed to write %s: %s', post_.file, e.message)

    def _queue_all(self, posts):
        """
        Add all posts in an iterable to the download queue.

        :param posts: The posts to add.
        """
        for post_ in posts:
            self._queue.append(post_)

    def download(self, posts, show_progress=False):
        """
        Download the files contained within a list of posts.

        :param posts: An iterable containing the posts to download. They will
                      be downloaded in order.
        :param show_progress: Whether to print a progress bar that updates as
                              the thread is downloading. Defaults to false.
        """
        global _interrupted
        _interrupted = False

        # populate the queue
        self._queue_all(posts)
        job_count = len(self._queue)

        # don't launch more threads than files
        threads = min(self._threads, len(self._queue))
        logger.debug('Will use %d threads for downloading', threads)

        # launch threads
        thread_pool = []
        target = functools.partial(Downloader.runner, self)
        start = datetime.datetime.now()
        for _ in range(threads):
            thread = threading.Thread(target=target)
            thread.start()
            thread_pool.append(thread)
        logger.debug('All threads launched')

        if show_progress:
            bar = Bar('Downloading',
                      max=job_count,
                      suffix='%(index)d/%(max)d - '
                             '%(elapsed_td)s elapsed, %(eta_td)s remaining')
            with _redirect_sigint():
                while len(self._completed_jobs) < job_count and \
                        not _interrupted:
                    bar.goto(len(self._completed_jobs))
                    time.sleep(.5)

        # wait for all threads to finish
        for i in range(threads):
            thread_pool[i].join()
        finish = datetime.datetime.now()

        if show_progress:
            # complete the progress bar if the queue is empty
            if not self._queue:
                # noinspection PyUnboundLocalVariable
                bar.goto(job_count)
            bar.finish()

        remaining_jobs = list(self._queue)
        return DownloadResult(self._completed_jobs,
                              remaining_jobs,
                              finish - start)
