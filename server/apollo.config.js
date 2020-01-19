const path = require('path');

/** @type { import('apollo').ApolloConfig } */
const config = {
    client: {
        includes: [],
        excludes: [],
        service: {
            name: 'turingarena-contest',
            localSchemaFile: path.resolve(__dirname, 'src/generated/graphql.schema.graphql'),
        },
    },
};

module.exports = config;
