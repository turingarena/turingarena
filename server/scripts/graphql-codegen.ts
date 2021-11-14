// tslint:disable: no-implicit-dependencies
import { generate } from '@graphql-codegen/cli';
import { readFileSync, writeFileSync } from 'fs';

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
                { add: { content: ['/* tslint:disable */'] } },
                { add: { content: [`import { Mapper } from '../main/mapper'`] } },
                // for some unknown reason graphql-code-generator used this type but didn't include it
                { add: { content: [`type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };`] } },
            ],
            config: {
                defaultMapper: 'Mapper<{T}>',
                contextType: '../main/api-context#ApiContext',
                rootValueType: '{}',
                noSchemaStitching: true,
                typesPrefix: '__generated_',
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

async function run() {
    await generate(config);
    const schemaBuffer = readFileSync(`src/generated/graphql.schema.json`);
    const schemaJson = schemaBuffer.toString();
    writeFileSync('src/generated/graphql.schema.ts', `export const graphqlIntrospection = ${schemaJson} as const;`);
}

run().catch(e => {
    console.error(e);
});
