import { gql } from 'apollo-server-core';
import { Resolvers } from '../main/resolver-types';
import { SubmitApi } from './submit';

export const mutationSchema = gql`
    type Mutation {
        init: Boolean!
        submit(submission: SubmissionInput!): Submission!
        logIn(token: String!): AuthResult
    }
`;

export interface MutationModelRecord {
    Mutation: {};
}

export const mutationResolvers: Resolvers = {
    Mutation: {
        init: async ({}, {}, ctx) => {
            await ctx.environment.sequelize.sync();

            return true;
        },
        submit: ({}, { submission }, ctx) => ctx.api(SubmitApi).submit(submission),
        logIn: ({}, { token }, ctx) => ctx.environment.authService.logIn(token),
    },
};
