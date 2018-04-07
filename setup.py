#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="turingarena",
    entry_points={
        "console_scripts": [
            "turingarena=turingarena.cli.main:main",
            "turingarena-sandbox=turingarena.sandbox.main:main",
            "turingarena-driver=turingarena.interface.driver.main:main",
        ],
        "pytest11": [
            "turingarena=turingarena.pytestplugin",
        ]
    },
)
