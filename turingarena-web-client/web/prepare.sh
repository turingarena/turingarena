#!/bin/sh
mkdir -p __generated__ &&
cargo run --package turingarena-core --bin turingarena-graphql-schema  > __generated__/graphql-schema.json &&
npm run codegen
