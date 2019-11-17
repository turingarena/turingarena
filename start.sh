#!/bin/bash

set +xe
echo 'Make sure you run `make` first.' >&2
cd rust/turingarena/examples/example-contest && bash start.sh
