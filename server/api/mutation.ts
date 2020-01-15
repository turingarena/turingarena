import { gql } from 'apollo-server-core';
import { Resolvers } from '../generated/graphql-types';

export const mutationSchema = gql`
    type Mutation {
        init: Query!
    }
`;

export const mutationResolvers: Resolvers = {
    Mutation: {
        init: async ({}, {}, ctx) => {
            await ctx.sequelize.sync();

            return {};
        },
    },
};
