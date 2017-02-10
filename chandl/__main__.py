#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import sys
import os
import argparse
import logging

import chandl
from chandl import util
from chandl.downloader import Downloader
from chandl.model.thread import Thread
from chandl.model import file


logger = logging.getLogger(__name__)


def _print_error(msg):
    """
    Print a string to stderr.

    :param msg: The message to print.
    """
    print(msg, file=sys.stderr)


def _construct_parser():
    parser = argparse.ArgumentParser(prog='chandl',
                                     description='A lightweight tool for '
                                                 'parsing and downloading '
                                                 '4chan threads.')
    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s ' + chandl.__version__)
    parser.add_argument('-v', '--verbosity',
                        help='increase output verbosity',
                        action='count',
                        default=0)
    parser.add_argument('-f', '--filter',
                        help='file types or extensions to download, value '
                             'either comma-separated or option passed multiple '
                             'times',
                        action='append',
                        type=util.decode_cli_arg,
                        nargs='?')
    parser.add_argument('-e', '--exclude',
                        help='file names to exclude, value either '
                             'comma-separated or option passed multiple times',
                        action='append',
                        type=util.decode_cli_arg,
                        default=[],
                        nargs='?')
    parser.add_argument('-o', '--output-dir',
                        help='the directory to create the `thread-dir` within',
                        nargs='?',
                        type=util.decode_cli_arg,
                        default=os.getcwd())
    parser.add_argument('-t', '--thread-dir',
                        help='relative to the `output-dir`, this will contain '
                             'downloaded files',
                        type=util.decode_cli_arg,
                        nargs='?')
    parser.add_argument('-n', '--name',
                        help='the format to use for downloaded file names',
                        nargs='?',
                        type=util.decode_cli_arg,
                        default='{file.id} - {file.name}.{file.extension}')
    parser.add_argument('-p', '--parallelism',
                        help='the maximum number of download threads to use '
                             'per core',
                        type=int,
                        default=2)
    parser.add_argument('url',
                        type=util.decode_cli_arg,
                        help='the URL of the thread to download')
    return parser


def _remove_unwanted(posts, args):

    # filter out posts without a file
    posts = [post for post in posts if post.has_file]
    logger.debug('%d contain a file', len(posts))

    # filter out files of the wrong type
    if args.filter:
        extensions = file.expand_filters(args.filter)
        posts = [post for post in posts if post.file.extension in extensions]
    logger.debug('%d are also of the desired format', len(posts))

    # filter out excluded file names
    filenames = util.expand_cli_args(args.exclude)
    posts = [post for post in posts if post.file.name not in filenames]
    logger.debug('%d have also not been excluded', len(posts))

    return posts


def main():
    """
    chandl's command-line entry point.
    """

    parser = _construct_parser()
    args = parser.parse_args()

    # sort out logging output and level
    level = util.log_level_from_vebosity(args.verbosity)
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    root.addHandler(handler)

    logger.debug(args)

    try:
        thread = Thread.from_url(args.url)
    except (ValueError, IOError) as e:
        _print_error('Error retrieving thread: {0}'.format(e))
        return 1

    posts = thread.posts
    logger.debug('Thread contains %d posts', len(posts))

    posts = _remove_unwanted(posts, args)
    logger.debug('Will download %d posts', len(posts))

    # check whether we still have anything to do
    if not posts:
        print('All files are either filtered out or excluded')
        return 0

    # use the first post to validate the --name
    try:
        post = posts[0]
        args.name.format(**post.__dict__)
    except KeyError as e:
        _print_error('Invalid file name specifier: {0}'.format(e))
        return 2

    # set an appropriate thread_dir if one was not specified
    if not args.thread_dir:
        args.thread_dir = util.make_filename(thread.title)

    # create --thread-dir
    write_dir = os.path.join(args.output_dir, args.thread_dir)
    if not os.path.isdir(write_dir):
        try:
            os.mkdir(write_dir, 0o700)
        except OSError as e:
            _print_error(
                'Failed to create the thread directory at {0}: {1}'.format(
                    write_dir, e))
            return 3

    # download the files
    print('Saving \'{0}\' to \'{1}\''.format(thread.title,
                                             os.path.relpath(write_dir,
                                                             os.getcwd())))
    downloader = Downloader(write_dir, args.name, args.parallelism)
    print(downloader.download(posts, level >= logging.WARNING))

    return 0


if __name__ == '__main__':
    status = main()
    logger.debug('Exiting with status %d', status)
    sys.exit(status)
