const path = require("path");

/** @type { import('apollo').ApolloConfig } */
const config = {
  client: {
    includes: ["./src/**/*.graphql"],
    excludes: [],
    service: {
      name: "turingarena-contest",
      localSchemaFile: path.resolve(
        __dirname,
        "__generated__/graphql-schema.json"
      )
    }
  }
};

module.exports = config;
