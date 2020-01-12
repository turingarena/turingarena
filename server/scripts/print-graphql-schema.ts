import { printSchema } from 'graphql';
import { buildSchemaFromTypeDefinitions } from 'graphql-tools';

import { typeDefs } from '../src/graphql';

const schema = buildSchemaFromTypeDefinitions(typeDefs);

console.log(printSchema(schema));
