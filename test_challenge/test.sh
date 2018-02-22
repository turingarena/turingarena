#!/usr/bin/env bash

set +ex

python setup.py install --force
python turingarena_setup.py

turingarena evaluate test_challenge:test_problem < entry.cpp
