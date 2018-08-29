#!/usr/bin/env python
import os

from setuptools import setup

setup(
    name='turingarena-cli',
    setup_requires=['pbr'],
    pbr='TURINGARENA_IS_DOCKER' not in os.environ,
)
