#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='picoredis',
    version='0.1.0',
    description='A very minimal Python Redis client library (not only) for MicroPython',
    author='Christopher Arndt',
    author_email='chris@chrisarndt.de',
    license='MIT',
    url='https://github.com/SpotlightKid/micropython-stm-lib',
    py_modules=['picoredis'],
    package_dir={'': 'picoredis'},
    zip_safe=False
)