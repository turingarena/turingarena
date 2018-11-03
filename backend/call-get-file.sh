#!/usr/bin/env bash

curl $1/get_file \
    -F file=$2
