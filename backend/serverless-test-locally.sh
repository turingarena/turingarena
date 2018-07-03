#!/usr/bin/env bash

HYPERSH_REGION=us-west-1 \
HYPERSH_FUNC_NAME=evaluate \
HYPERSH_FUNC_ID=3a85dc1d-47e9-453c-bbab-f33abc521197 \
python -m turingarena_impl.api.serve
