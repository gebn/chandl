#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys
import os
import argparse
import logging
from datetime import datetime

import chandl
from chandl import util
from chandl.downloader import Downloader
from chandl.model.thread import Thread
from chandl.model.post import Post


logger = logging.getLogger(__name__)


def main():
    """
    Chandl entry point.
    """
    parser = argparse.ArgumentParser(prog='chandl',
                                     description='A lightweight tool for '
                                                 'parsing and downloading '
                                                 '4chan threads.')
    parser.add_argument('url',
                        nargs='+',
                        type=util.decode_cli_arg,
                        help='the URL(s) of the thread(s) whose files to '
                             'download')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + chandl.__version__)
    parser.add_argument('-c', '--cwd',
                        action='store_true',
                        default=False,
                        help='download to the working directory')
    parser.add_argument('-p', '--parallelism',
                        type=int,
                        help='the maximum number of download threads to use '
                             'per core',
                        default=5)
    parser.add_argument('-v', '--verbosity',
                        help='increase output verbosity',
                        action='count',
                        default=0)
    args = parser.parse_args()

    # sort out logging output and level
    level = util.log_level_from_vebosity(args.verbosity)
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    root.addHandler(handler)

    for url in args.url:
        try:
            thread = Thread.from_url(url)
        except ValueError as e:
            # almost definitely invalid url
            print(e, file=sys.stderr)

        print('Downloading {0}'.format(
            thread.subject if thread.subject else str(thread.id)))
        files = list(thread.posts.filter(lambda p: p.has_file).map(
            lambda post: post.file))  # list() as we need to rewind

        if args.cwd:
            directory = os.getcwd()
        else:
            directory = util.make_filename(thread.subject) if thread.subject \
                else str(thread.id)
            if not os.path.exists(directory):
                os.mkdir(directory)

        logger.debug('Downloading to %s', directory)

        dl = Downloader(directory,
                        lambda image: str(image.id) + '.' + image.extension,
                        parallelism=args.parallelism)
        start = datetime.now()
        dl.download(files)
        finish = datetime.now()

        size = sum([file_.size for file_ in files])
        delta = finish - start
        print('Downloaded {0} in {1:0.3f} seconds ({2}/s)'.format(
            util.bytes_fmt(size),
            delta.total_seconds(),
            util.bytes_fmt(size / delta.total_seconds())))


if __name__ == '__main__':
    main()
