#!/usr/bin/env bash

curl $1/evaluate \
    -F packs[]=d1a18623594c47621e9289767bc3ce997ce45756 \
    -F evaluator_cmd="/usr/local/bin/python -u evaluator.py" \
    -F submission[source]=@../examples/sum_of_two_numbers/solutions/correct.cpp \
    -F repositories[main][type]=git_clone \
    -F repositories[main][url]=https://github.com/turingarena/turingarena.git
