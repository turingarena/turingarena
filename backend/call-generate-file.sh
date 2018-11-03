#!/usr/bin/env bash

curl $1/generate_file \
    -F oid=FETCH_HEAD \
    -F repositories[url]=https://github.com/turingarena/turingarena.git
