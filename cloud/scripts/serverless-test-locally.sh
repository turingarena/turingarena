#!/usr/bin/env bash

HYPERSH_REGION=us-west-1 \
DYNAMODB_TABLE=turingarena-branch-develop-table \
python -m turingarena.api.serve
