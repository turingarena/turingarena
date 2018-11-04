#!/usr/bin/env python

from setuptools import setup

with open("requirements.txt") as f:
    install_requires = f.read()

setup(install_requires=install_requires)
