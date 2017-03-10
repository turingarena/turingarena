#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Build and installation routines for task-wizard.

"""

import io
import re
import os

from setuptools import setup, find_packages


setup(
    name="task-wizard",
    version="0.2",
    author="",
    author_email="",
    url="",
    download_url="",
    description="",
    entry_points={
        "console_scripts": [
            "taskcc=taskwizard.compiler.compiler:main",
        ],
    },
    packages=find_packages(),
    keywords="",
    license="",
    classifiers=[],
)
