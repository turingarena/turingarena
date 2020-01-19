// tslint:disable: no-implicit-dependencies
import { generate } from '@graphql-codegen/cli';

type CodegenConfig = Parameters<typeof generate>[0];

const modelNames = ['User', 'Contest', 'FileContent'];
const mappers = Object.fromEntries(
    modelNames.map(name => [name, `ModelRecord['${name}']`]),
);

const config: CodegenConfig = {
    schema: `scripts/graphql-schema.ts`,
    documents: `src/core/*.ts`,
    overwrite: true,
    watch: process.argv.includes('--watch'),
    generates: {
        'src/generated/graphql-types.ts': {
            plugins: [
                'typescript',
                'typescript-resolvers',
                'typescript-operations',
                {
                    add: '/* tslint:disable */',
                },
                {
                    add: `import { ModelRecord } from '../main/context';`,
                },
            ],
            config: {
                defaultMapper: 'any',
                mappers,
                contextType: '../main/context#ApiContext',
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
