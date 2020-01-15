import { gql } from 'apollo-server-core';
import { IResolvers, makeExecutableSchema } from 'graphql-tools';
import { Resolvers } from '../generated/graphql-types';
import { mutationResolvers, mutationSchema } from './mutation';
import { queryResolvers, querySchema } from './query';
import { userSchema } from './user';

export const schema = gql`
    ${querySchema}
    ${mutationSchema}
    ${userSchema}
`;

export const resolvers: Resolvers = {
    ...queryResolvers,
    ...mutationResolvers,
};

export const executableSchema = makeExecutableSchema({
    typeDefs: schema,
    resolvers: resolvers as IResolvers,
});

// tslint:disable-next-line: no-default-export
export default schema; // For graphql-codegen
