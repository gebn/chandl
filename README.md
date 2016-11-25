# chandl

[![PyPI](https://img.shields.io/pypi/v/chandl.svg)](https://pypi.python.org/pypi/chandl)
![MIT License](https://img.shields.io/pypi/l/chandl.svg)

A lightweight tool for parsing and downloading 4chan threads.

## Features

 - An API for programmatically analysing 4chan content.
 - Customise the each file name using a lambda function.
 - Filter out images or videos.
 - Concurrent downloading, with parallelism linked to the number of cores.

## Dependencies

 - Python 2.7.x, 3.4.x or 3.5.x
 - six

## Installation

To install `chandl`, simply run:

    $ pip install chandl

## Usage

    $ python -m chandl -h
    usage: chandl [-h] [-c] [-t THREADS] [-v] url [url ...]

    A lightweight tool for parsing and downloading 4chan threads.

    positional arguments:
      url                   the URL(s) of the thread(s) whose files to download

    optional arguments:
      -h, --help            show this help message and exit
      -c, --cwd             download to the working directory
      -t THREADS, --threads THREADS
                            the maximum number of download threads to use per core
      -v, --verbosity       increase output verbosity

## Roadmap

 - Check compatibility
 - Add tests and CI
