chandl
======

.. image:: https://img.shields.io/pypi/status/chandl.svg
   :target: https://pypi.python.org/pypi/chandl
.. image:: https://img.shields.io/pypi/v/chandl.svg
   :target: https://pypi.python.org/pypi/chandl
.. image:: https://img.shields.io/pypi/pyversions/chandl.svg
   :target: https://pypi.python.org/pypi/chandl
.. image:: https://travis-ci.org/gebn/chandl.svg?branch=master
   :target: https://travis-ci.org/gebn/chandl
.. image:: https://scan.coverity.com/projects/11734/badge.svg
   :target: https://scan.coverity.com/projects/gebn-chandl
.. image:: https://coveralls.io/repos/github/gebn/chandl/badge.svg?branch=master
   :target: https://coveralls.io/github/gebn/chandl?branch=master

A lightweight tool for parsing and downloading 4chan threads.

Features
--------

-  A comprehensive API for programmatically analysing 4chan content.
-  Concurrent downloading, with parallelism linked to the number of available cores.
-  Override the file naming scheme and specify exclusions for thread downloads.
-  Filter files by extension or category (e.g. images, videos).

Installation
------------

To install ``chandl``, simply run:

::

    $ pip install chandl

Examples
--------

Download all files in ``<thread_url>``, to a new directory named after the thread if possible, otherwise its raw id:

::

    $ chandl <thread_url>

Download all images and ``.webm`` files in ``<thread_url>`` to ``/dev/shm``, using 3 download threads per core:

::

    $ chandl -f images,webm -o /dev/shm -p 3 <thread_url>

Download all files in ``<thread_url>``, except ``abc.jpg`` and ``def.jpg`` to the present working directory, using a custom name format:

::

    $ chandl -e abc.jpg,def.jpg -t . -n "{board} - {file.name}.{file.extension}" <thread_url>

Usage
-----

::

    $ chandl -h
    usage: chandl [-h] [-V] [-v] [-f [FILTER]] [-e [EXCLUDE]] [-o [OUTPUT_DIR]]
                  [-t [THREAD_DIR]] [-n [NAME]] [-p PARALLELISM]
                  url

    A lightweight tool for parsing and downloading 4chan threads.

    positional arguments:
      url                   the URL of the thread to download

    optional arguments:
      -h, --help            show this help message and exit
      -V, --version         show program's version number and exit
      -v, --verbosity       increase output verbosity
      -f [FILTER], --filter [FILTER]
                            file types or extensions to download, value either
                            comma-separated or option passed multiple times
      -e [EXCLUDE], --exclude [EXCLUDE]
                            file names to exclude, value either comma-separated or
                            option passed multiple times
      -o [OUTPUT_DIR], --output-dir [OUTPUT_DIR]
                            the directory to create the `thread-dir` within
      -t [THREAD_DIR], --thread-dir [THREAD_DIR]
                            relative to the `output-dir`, this will contain
                            downloaded files
      -n [NAME], --name [NAME]
                            the format to use for downloaded file names
      -p PARALLELISM, --parallelism PARALLELISM
                            the maximum number of download threads to use per core

Roadmap
-------

-  Implement tracking of threads until they are deleted
-  Improve test coverage
-  Pylint or flake8 integration
