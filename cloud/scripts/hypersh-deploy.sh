#!/usr/bin/env bash

hyper func rm hypersh-api-test
hyper func create \
    --name hypersh-api-test \
    --env AWS_DEFAULT_REGION=$(aws configure get region) \
    --env AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id) \
    --env AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key) \
    turingarena/turingarena:develop \
    python -m turingarena.api.hypersh_api
