chandl
======

.. image:: https://img.shields.io/pypi/v/chandl.svg
   :target: https://pypi.python.org/pypi/chandl
.. image:: https://img.shields.io/pypi/pyversions/chandl.svg
.. image:: https://travis-ci.org/gebn/chandl.svg?branch=master
   :target: https://travis-ci.org/gebn/chandl
.. image:: https://coveralls.io/repos/github/gebn/chandl/badge.svg?branch=master
   :target: https://coveralls.io/github/gebn/chandl?branch=master

A lightweight tool for parsing and downloading 4chan threads.

Features
--------

-  An API for programmatically analysing 4chan content.
-  Customise the each file name using a lambda function.
-  Filter out images or videos.
-  Concurrent downloading, with parallelism linked to the number of
   cores.

Installation
------------

To install ``chandl``, simply run:

::

    $ pip install chandl

Usage
-----

::

    $ chandl -h
    usage: chandl [-h] [--version] [-c] [-p PARALLELISM] [-v] url [url ...]

    A lightweight tool for parsing and downloading 4chan threads.

    positional arguments:
      url                   the URL(s) of the thread(s) whose files to download

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      -c, --cwd             download to the working directory
      -p PARALLELISM, --parallelism PARALLELISM
                            the maximum number of download threads to use per core
      -v, --verbosity       increase output verbosity

Roadmap
-------

-  Implement tracking of threads until they are deleted
-  File exclusion
-  Improve test coverage
-  Pylint or flake8 integration
