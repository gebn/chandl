# -*- coding: utf-8 -*-
import codecs
from setuptools import setup, find_packages


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
    version='0.0.1',
    description='A lightweight tool for parsing and downloading 4chan threads.',
    long_description=_read_file('README.md'),
    license='MIT',
    url='https://github.com/gebn/chandl',
    author='George Brighton',
    author_email='oss@gebn.co.uk',
    packages=find_packages(),
    install_requires=[
        'six>=1.9.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ]
)
