import { gql } from 'apollo-server-core';
import { Resolvers } from '../main/resolver-types';
import { Contest } from './contest';
import { SubmitApi } from './submit';

export const mutationSchema = gql`
    type Mutation {
        init: Boolean!

        createContest(contest: ContestInput!): Boolean!
        updateContest(contest: ContestInput!): Boolean!
        deleteContest(contest: ID!): Boolean!

        # createFile(file: FileContentInput!): Boolean!
        # deleteFile(id: ID!): Boolean!

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
        createContest: async ({}, { contest }, ctx) => {
            await ctx.table(Contest).create(contest);

            return true;
        },
        updateContest: async ({}, { contest }, ctx) => true, // TODO
        deleteContest: async ({}, { contest }, ctx) => {
            await ctx.table(Contest).destroy({
                where: {
                    name,
                },
            });

            return true;
        },
        submit: ({}, { submission }, ctx) => ctx.api(SubmitApi).submit(submission),
        logIn: ({}, { token }, ctx) => ctx.environment.authService.logIn(token),
    },
};
