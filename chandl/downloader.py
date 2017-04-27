# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

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


def _handle_sigint(number, frame):
    """
    Called when we receive a SIGINT.

    :param number: The signal number (2 in this case).
    :param frame: The stack frame.
    """
    del number, frame
    global _interrupted
    _interrupted = True


@contextlib.contextmanager
def _redirect_sigint(handler=_handle_sigint):
    """
    For the duration of this function, a SIGINT will call _handle_sigint()
    rather than the normal Python routine.

    :param handler: The function to invoke if SIGINT is received.
    """
    original_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, handler)
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

    def __init__(self, downloaded_jobs, failed_jobs, skipped_jobs,
                 remaining_jobs, elapsed):
        """
        Initialise a new download result.

        :param downloaded_jobs: A list of posts that downloaded successfully.
        :param failed_jobs: A list of posts that failed to download.
        :param skipped_jobs: A list of posts that were skipped because the file
                             already existed.
        :param remaining_jobs: Jobs yet to be processed when the download was
                               cancelled.
        :param elapsed: A timedelta representing the duration of the download.
        """
        self.downloaded_bytes = self._posts_size(downloaded_jobs)
        self.failed_bytes = self._posts_size(failed_jobs)
        self.skipped_bytes = self._posts_size(skipped_jobs)
        self.remaining_bytes = self._posts_size(remaining_jobs)
        self.total_bytes = self.downloaded_bytes + \
            self.failed_bytes + \
            self.skipped_bytes + \
            self.remaining_bytes

        self.downloaded_job_count = len(downloaded_jobs)
        self.failed_job_count = len(failed_jobs)
        self.skipped_job_count = len(skipped_jobs)
        self.remaining_job_count = len(remaining_jobs)
        self.total_jobs = self.downloaded_job_count + \
            self.failed_job_count + \
            self.skipped_job_count + \
            self.remaining_job_count

        self.downloaded_jobs = downloaded_jobs
        self.failed_jobs = failed_jobs
        self.skipped_jobs = skipped_jobs
        self.remaining_jobs = remaining_jobs
        self.elapsed = elapsed

    def __str__(self):
        """
        Get a formatted representation of this download's outcome.

        :return: The download statistics as a human-readable string.
        """
        string = '{0}/{1} jobs completed, {2} failed, {3} skipped{4}'.format(
            self.downloaded_job_count + self.skipped_job_count,
            self.total_jobs,
            self.failed_job_count,
            self.skipped_job_count,
            os.linesep)
        string += '{0}/{1} downloaded, {2} skipped{3}'.format(
            util.bytes_fmt(self.downloaded_bytes),
            util.bytes_fmt(self.total_bytes),
            util.bytes_fmt(self.skipped_bytes),
            os.linesep)
        string += 'Duration: {0:0.3f} seconds ({1}/s)'.format(
            self.elapsed.total_seconds(),
            util.bytes_fmt(int((self.downloaded_bytes + self.skipped_bytes) //
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

        self._downloaded_jobs_lock = threading.Lock()
        self._downloaded_jobs = []

        self._failed_jobs_lock = threading.Lock()
        self._failed_jobs = []

        self._skipped_jobs_lock = threading.Lock()
        self._skipped_jobs = []

    # noinspection PyProtectedMember
    @staticmethod
    def runner(downloader):
        """
        A single thread's execution.

        :param downloader: The downloader instance the thread belongs to.
        """
        session = requests.Session()
        while not _interrupted:
            try:
                post_ = downloader._queue.popleft()
                Downloader.handle(downloader, post_, session)
            except IndexError:
                # no items left to process - let function return
                break

    # noinspection PyProtectedMember
    @staticmethod
    def handle(downloader, post_, session):
        """
        Downloads the file in a post.

        :param downloader: The downloader context.
        :param post_: The post to download.
        :param session: The requests session to use for the download.
        """
        try:
            name = downloader._name_fmt.format(**post_.__dict__)
            existed = post_.file.save_to(downloader._directory, name,
                                         session=session)
            if existed:
                with downloader._skipped_jobs_lock:
                    downloader._skipped_jobs.append(post_)
            else:
                with downloader._downloaded_jobs_lock:
                    downloader._downloaded_jobs.append(post_)
        except IOError as e:
            logger.exception('Failed to write %s: %s', post_.file, str(e))
            with downloader._failed_jobs_lock:
                downloader._failed_jobs.append(post_)

    def _queue_all(self, posts):
        """
        Add all posts in an iterable to the download queue.

        :param posts: The posts to add.
        """
        for post_ in posts:
            self._queue.append(post_)

    def download(self, posts, interactive=False):
        """
        Download the files contained within a list of posts.

        :param posts: An iterable containing the posts to download. They will
                      be downloaded in order.
        :param interactive: Whether to print a progress bar that updates as
                            the thread is downloading, and display a message if
                            the process is interrupted. Defaults to false.
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

        if interactive:
            progress = Bar('Downloading',
                           max=job_count,
                           suffix='%(index)d/%(max)d - %(elapsed_td)s elapsed, '
                                  '%(eta_td)s remaining')
            with _redirect_sigint():
                while self._queue and not _interrupted:
                    progress.goto(len(self._downloaded_jobs) +
                                  len(self._failed_jobs) +
                                  len(self._skipped_jobs))
                    time.sleep(.5)

        if interactive and _interrupted:
            # the act of C-c does not print a line break; we do not want a
            # continuation of the previous line
            print(os.linesep + 'Interrupted; waiting for download threads to '
                               'finish their current jobs. This may take a few '
                               'seconds.')

        # wait for all threads to finish
        for i in range(threads):
            thread_pool[i].join()
        finish = datetime.datetime.now()

        if interactive:
            # complete the progress bar if the queue is empty
            if not self._queue:
                # noinspection PyUnboundLocalVariable
                progress.goto(job_count)
            progress.finish()

        return DownloadResult(self._downloaded_jobs,
                              self._failed_jobs,
                              self._skipped_jobs,
                              list(self._queue),
                              finish - start)
