#!/usr/bin/env python
import os

from setuptools import setup

use_pbr = 'TURINGARENA_IS_DOCKER' not in os.environ
if use_pbr:
    setup_requires = ['pbr']
else:
    setup_requires = []

setup(
    name='turingarena-cli',
    setup_requires=setup_requires,
    pbr=use_pbr,
)
