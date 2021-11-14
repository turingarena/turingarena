import { makeExecutableSchema } from 'graphql-tools';
import { schema } from '../core';

/** Executable schema, obtained combining full GraphQL schema and resolvers. */
export const executableSchema = makeExecutableSchema({ typeDefs: schema });
