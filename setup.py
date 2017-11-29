#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Build and installation routines for task-wizard.

"""

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
            "turingarena=turingarena.cli.main:main",
        ],
    },
    packages=find_packages(),
    keywords="",
    license="",
    classifiers=[],
    install_requires=[
        "docopt",
        "tatsu",
        "pyyaml",
        "coloredlogs",
        "bidict",
        "gitpython",
    ],
    tests_require=[
        "pytest",
    ],
    zip_safe=False,
)
