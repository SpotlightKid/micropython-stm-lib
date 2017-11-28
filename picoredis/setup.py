#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from io import open
from setuptools import setup


def read(*paths):
    with open(os.path.join(*paths), encoding='utf-8') as fp:
        return fp.read()


classifiers = """\
Development Status :: 3 - Alpha
Environment :: Other Environment
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: POSIX
Operating System :: POSIX :: Linux
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: MicroPython
Programming Language :: Python :: Implementation :: PyPy
Topic :: Database
Topic :: Home Automation
Topic :: Software Development :: Libraries :: Python Modules
Topic :: System :: Networking
"""


setup(
    name='picoredis',
    version='0.1.0',
    author='Christopher Arndt',
    author_email='chris@chrisarndt.de',
    description='A very minimal Python Redis client library (not only) for MicroPython',
    long_description=read('README.rst'),
    license='MIT',
    url='https://github.com/SpotlightKid/micropython-stm-lib',
    keywords='database,micropython,redis,network',
    classifiers=[c for c in (c.strip() for c in classifiers.splitlines())
                 if c and not c.startswith('#')],
    py_modules=['picoredis'],
    package_dir={'': 'picoredis'},
    zip_safe=True
)
