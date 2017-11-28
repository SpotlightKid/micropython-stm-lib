#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from io import open
from setuptools import setup


def read(*paths):
    with open(os.path.join(*paths), encoding='utf-8') as fp:
        return fp.read()


setup(
    name='picoredis',
    version='0.1.0',
    description='A very minimal Python Redis client library (not only) for MicroPython',
    long_description=read('README.md'),
    keywords='database,micropython,redis,network',
    author='Christopher Arndt',
    author_email='chris@chrisarndt.de',
    license='MIT',
    url='https://github.com/SpotlightKid/micropython-stm-lib',
    py_modules=['picoredis'],
    package_dir={'': 'picoredis'},
    zip_safe=True
)
