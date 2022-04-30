import { makeExecutableSchema } from 'graphql-tools';
import { schema } from '../core/schema';

/** Executable schema, obtained combining full GraphQL schema and resolvers. */
/* FIXME: callable to avoid circular dependencies. */
export const executableSchema = () =>
    makeExecutableSchema({
        typeDefs: schema,
        resolverValidationOptions: {
            requireResolversForResolveType: false,
        },
    });
