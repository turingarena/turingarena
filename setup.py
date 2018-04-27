#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="turingarena",
    entry_points={
        "console_scripts": [
            "turingarena=turingarena_impl.cli.main:main",
            "turingarena-sandbox=turingarena_impl.sandbox.main:main",
            "turingarena-driver=turingarena_impl.interface.driver.main:main",
        ],
        "pytest11": [
            "turingarena=turingarena_impl.pytestplugin",
        ]
    },
)
