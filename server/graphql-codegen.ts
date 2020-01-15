// tslint:disable: no-implicit-dependencies
import { generate } from '@graphql-codegen/cli';

type CodegenConfig = Parameters<typeof generate>[0];

const modelNames = ['User', 'Contest'];
const mappers = Object.fromEntries(modelNames.map((name) => [
    name, `ModelRecord['${name}']`,
]));

const config: CodegenConfig = {
    schema: `api/index.ts`,
    documents: `api/*.ts`,
    overwrite: true,
    generates: {
        'generated/graphql-types.ts': {
            plugins: [
                'typescript',
                'typescript-resolvers',
                'typescript-operations',
                {
                    add: '/* tslint:disable */',
                },
                {
                    add: `import { ModelRecord } from '../api/index';`,
                },
            ],
            config: {
                defaultMapper: 'any',
                mappers,
                contextType: '../api/index#ApiContext',
            },
        },
        'generated/graphql.schema.json': {
            plugins: ['introspection'],
        },
        'generated/graphql.schema.graphql': {
            plugins: ['schema-ast'],
        },
    },
    require: 'ts-node/register/transpile-only',
};

generate(config).catch((e) => {
    console.error(e);
});
