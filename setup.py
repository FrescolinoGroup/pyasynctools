#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from setuptools import setup

pkgname = 'async_tools'
pkgname_qualified = 'fsc.' + pkgname

with open('doc/description.txt', 'r') as f:
    description = f.read()
try:
    with open('doc/README', 'r') as f:
        readme = f.read()
except IOError:
    readme = description

with open('version.txt', 'r') as f:
    version = f.read().strip()

if sys.version_info < (3, 5):
    raise "Must use at least Python version 3.5"

setup(
    name=pkgname_qualified.replace('_', '-'),
    version=version,
    packages=[pkgname_qualified],
    url='http://frescolinogroup.github.io/frescolino/pyasynctools/' +
    '.'.join(version.split('.')[:2]),
    include_package_data=True,
    author='C. Frescolino',
    author_email='frescolino@lists.phys.ethz.ch',
    description=description,
    install_requires=['fsc.export'],
    extras_require={
        'dev': [
            'pytest', 'pytest-cov', 'yapf==0.22.0', 'prospector', 'pre-commit',
            'pylint', 'sphinx', 'sphinx-rtd-theme', 'ipython>=6.2',
            'matplotlib'
        ]
    },
    long_description=readme,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3', 'Topic :: Utilities'
    ],
    license='Apache',
)
