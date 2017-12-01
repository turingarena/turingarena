#!/usr/bin/env bash

python setup.py install --force
python turingarena_setup.py

REPO_PATH=$HOME/.turingarena/db.git
mkdir -p $REPO_PATH

git init --bare $REPO_PATH

ENTRY=$(turingarena entry --repo-path=$REPO_PATH --file=entry.cpp:entry.cpp)

turingarena make --module=test_challenge --name=problem make --phase=evaluate_goal --repo-path=$REPO_PATH --entry=entry_entry:$ENTRY
