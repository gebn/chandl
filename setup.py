# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import codecs

with codecs.open('LICENSE') as f:
    license_ = f.read()

setup(
    name='chandl',
    version='0.0.1',
    description='A lightweight tool for parsing and downloading 4chan threads.',
    license=license_,
    url='https://github.com/gebn/chandl',
    author='George Brighton',
    author_email='os@gebn.co.uk',
    packages=find_packages(),
    install_requires=[
        'six'
    ]
)
