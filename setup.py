#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
            "turingarena-sandbox=turingarena.sandbox.main:main",
            "turingarena-driver=turingarena.interface.driver.main:main",
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
        "psutil",
    ],
    tests_require=[
        "pytest",
    ],
    zip_safe=False,
)
