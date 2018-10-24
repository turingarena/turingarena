#!/usr/bin/env bash

HYPERSH_REGION=us-west-1 \
DYNAMODB_EVALUATION_EVENTS_TABLE=turingarena-branch-develop-EvaluationEventsTable \
python -m turingarena_impl.api.serve
