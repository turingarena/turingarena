#!/usr/bin/env bash

curl $1/generate_file \
    -F oid=d1a18623594c47621e9289767bc3ce997ce45756 \
    -F repository[url]=https://github.com/turingarena/turingarena.git
