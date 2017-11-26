#!/usr/bin/env bash

python setup.py develop

turingarena protocol --name test_challenge install
turingarena protocol --name test_challenge proxy
turingarena protocol --name test_challenge skeleton

turingarena make --module test_challenge --name problem run --phase compile_entry
turingarena make --module test_challenge --name problem run --phase goal_goal
