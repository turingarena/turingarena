#!/bin/sh

cargo run --package turingarena-core --bin turingarena-graphql-schema  > graphql-schema.json
npm run codegen

