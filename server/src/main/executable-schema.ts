import { IResolvers, makeExecutableSchema } from 'graphql-tools';
import { resolvers, schema } from '../core';

/** Executable schema, obtained combining full GraphQL schema and resolvers. */
export const createSchema = () =>
    makeExecutableSchema({
        typeDefs: schema,
        resolvers: resolvers as IResolvers,
    });
