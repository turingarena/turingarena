#!/usr/bin/env bash

python setup.py develop

turingarena protocol --name test_challenge install
turingarena protocol --name test_challenge proxy
turingarena protocol --name test_challenge skeleton

turingarena sandbox compile \
    --protocol test_challenge \
    --interface exampleinterface \
    -x c++ -o entry entry.cpp

turingarena problem --module test_challenge \
    goal --name goal evaluate
