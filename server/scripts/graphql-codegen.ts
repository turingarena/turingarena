// tslint:disable: no-implicit-dependencies
import { generate } from '@graphql-codegen/cli';

type CodegenConfig = Parameters<typeof generate>[0];

const config: CodegenConfig = {
    schema: `scripts/graphql-schema.ts`,
    documents: `src/core/*.ts`,
    overwrite: true,
    watch: process.argv.includes('--watch'),
    generates: {
        'src/generated/graphql-types.ts': {
            plugins: [
                {
                    typescript: {
                        avoidOptionals: false,
                        nonOptionalTypename: true,
                        enumsAsTypes: true,
                    },
                },
                'typescript-resolvers',
                'typescript-operations',
                {
                    add: '/* tslint:disable */',
                },
            ],
            config: {
                defaultMapper: 'any',
                contextType: '../main/api-context#ApiContext',
                rootValueType: 'any',
                noSchemaStitching: true,
            },
        },
        'src/generated/graphql.schema.json': {
            plugins: ['introspection'],
        },
        'src/generated/graphql.schema.graphql': {
            plugins: ['schema-ast'],
        },
    },
    require: 'ts-node/register/transpile-only',
};

generate(config).catch(e => {
    console.error(e);
});
