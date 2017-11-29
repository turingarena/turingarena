#!/usr/bin/env bash

python setup.py install --force

python turingarena_setup.py

turingarena make --module test_challenge --name problem run --phase compile_entry
turingarena make --module test_challenge --name problem run --phase goal_goal
