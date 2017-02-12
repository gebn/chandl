# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from setuptools import setup, find_packages
import codecs

import chandl


def _read_file(name, encoding='utf-8'):
    """
    Read the contents of a file.

    :param name: The name of the file in the current directory.
    :param encoding: The encoding of the file; defaults to utf-8.
    :return: The contents of the file.
    """
    with codecs.open(name, encoding=encoding) as f:
        return f.read()


setup(
    name='chandl',
    version=chandl.__version__,
    description='A lightweight tool for parsing and downloading 4chan threads.',
    long_description=_read_file('README.rst'),
    license='MIT',
    url='https://github.com/gebn/chandl',
    author='George Brighton',
    author_email='oss@gebn.co.uk',
    packages=find_packages(),
    install_requires=[
        'six>=1.9.0',
        'Unidecode',
        'requests',
        'httmock',
        'progress',
        'pytz',
        'pyfakefs'
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={
        'console_scripts': [
            'chandl = chandl.__main__:main',
        ]
    }
)
