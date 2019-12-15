test -f __generated__/graphql-schema.json ||
  {
    mkdir -p __generated__ &&
    cargo run --features contest --bin turingarena-graphql-schema  > __generated__/graphql-schema.json
  }
exit $?
