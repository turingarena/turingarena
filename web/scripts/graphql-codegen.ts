// tslint:disable: no-implicit-dependencies
import { generate } from '@graphql-codegen/cli';

type CodegenConfig = Parameters<typeof generate>[0];

const config: CodegenConfig = {
  schema: `../server/src/generated/graphql.schema.graphql`,
  documents: `src/**/*.ts`,
  overwrite: true,
  watch: process.argv.includes('--watch'),
  generates: {
    'src/generated/graphql-types.ts': {
      plugins: [
        {
          typescript: {
            avoidOptionals: true,
            nonOptionalTypename: true,
          },
        },
        'typescript-operations',
        {
          add: '/* tslint:disable */',
        },
      ],
    },
  },
  require: 'ts-node/register/transpile-only',
};

generate(config).catch(e => {
  console.error(e);
});
