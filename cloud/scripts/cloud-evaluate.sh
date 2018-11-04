#!/usr/bin/env bash

ENDPOINT=$1
SOURCE=$2

turingarena cloud evaluate source:$SOURCE --oid cb2dc5bd8c19bcbf461df17967e507794f1ee128 --repository https://github.com/turingarena/turingarena.git --log-level=debug --endpoint $ENDPOINT
