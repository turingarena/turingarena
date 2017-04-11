#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Build and installation routines for task-wizard.

"""

import io
import os
import re
from setuptools import setup, find_packages


setup(
    name="taskwizard",
    version="0.2",
    author="",
    author_email="",
    url="",
    download_url="",
    description="",
    entry_points={
        "console_scripts": [
            "taskwizard=taskwizard.main:main",
        ],
    },
    packages=find_packages(),
    package_data={
        'taskwizard': ['**/templates/**', '**/*static/**'],
    },
    keywords="",
    license="",
    classifiers=[],
    install_requires=[
        "docopt",
        "grako>=3.20",
        "jinja2",
        "pyyaml",
    ],
)
