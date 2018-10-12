#!/usr/bin/env bash

python -m turingarena_impl.api.make_hypersh_request $1 | sudo docker run \
    --rm \
    -i \
    --mount=type=bind,src=$(dirname $(realpath $0))/..,dst=/usr/local/turingarena/,readonly \
    --env AWS_DEFAULT_REGION=$(aws configure get region) \
    --env AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id) \
    --env AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key) \
    --env DYNAMODB_EVALUATION_EVENTS_TABLE=turingarena-branch-develop-EvaluationEventsTable \
    --env DYNAMODB_SUBMISSIONS_TABLE=turingarena-branch-develop-SubmissionsTable \
    turingarena/turingarena \
    python -m turingarena_impl.api.hypersh_evaluate