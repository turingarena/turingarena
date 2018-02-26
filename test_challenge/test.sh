#!/usr/bin/env bash

set +ex

python setup.py develop

turingarena evaluate test_challenge:test_problem < entry.cpp
