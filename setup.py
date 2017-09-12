#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Build and installation routines for task-wizard.

"""

import io
import os
import re
from setuptools import setup, find_packages


setup(
    name="turingarena",
    version="0.2",
    author="",
    author_email="",
    url="",
    download_url="",
    description="",
    entry_points={
        "console_scripts": [
            "turingarenac=turingarena.compiler.main:main",
            "turingarenasandbox=turingarena.sandbox.main:main",
        ],
    },
    packages=find_packages(),
    package_data={
        'turingarena': ['**/templates/**', '**/*static/**'],
    },
    keywords="",
    license="",
    classifiers=[],
    install_requires=[
        "docopt",
        "tatsu",
        "jinja2",
        "pyyaml",
        "coloredlogs",
    ],
)
