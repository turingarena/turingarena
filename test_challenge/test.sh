#!/usr/bin/env bash

python setup.py install --force
python turingarena_setup.py

REPO_PATH=$HOME/.turingarena/db.git
mkdir -p $REPO_PATH

git init --bare $REPO_PATH

ENTRY=$(turingarena make entry --plan=test_challenge:problem --repo-path=$REPO_PATH entry_entry --file=entry.cpp:entry.cpp)

turingarena make make --plan=test_challenge:problem --repo-path=$REPO_PATH --entry=entry_entry:$ENTRY evaluate_goal
