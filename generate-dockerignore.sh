#!/usr/bin/env bash

( echo '**' ; for f in $(git ls-files); do echo '!'$f ; done ) > .dockerignore
