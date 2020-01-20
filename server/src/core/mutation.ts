import { gql } from 'apollo-server-core';
import { Resolvers } from '../generated/graphql-types';
import { Contest, contestMutationResolvers } from './contest';
import { Problem } from './problem';
import { User } from './user';

export const mutationSchema = gql`
    type Mutation {
        init: Boolean!
        createUser(user: UserInput!): Boolean!
        updateUser(user: UserInput!): Boolean!
        deleteUser(user: ID!): Boolean!
        createProblem(problem: ProblemInput!): Boolean!
        deleteProblem(problem: ID!): Boolean!
        updateProblem(problem: ProblemInput!): Boolean!
        createContest(contest: ContestInput!): Boolean!
        updateContest(contest: ContestInput!): Boolean!
        deleteContest(contest: ID!): Boolean!
        createFile(file: FileContentInput!): Boolean!
        deleteFile(hash: ID!): Boolean!

        addProblem(contestName: ID!, name: ID!): Boolean!
        removeProblem(contestName: ID!, name: ID!): Boolean!
        addUser(contestName: ID!, username: ID!): Boolean!
        removeUser(contestName: ID!, username: ID!): Boolean!
        submit(contestName: ID!, username: ID!, problemName: ID!, submission: SubmissionInput!): Boolean!
    }
`;

export const mutationResolvers: Resolvers = {
    Mutation: {
        init: async ({}, {}, ctx) => {
            await ctx.sequelize.sync();

            return true;
        },
        updateUser: async ({}, { user }, ctx) => true, // TODO
        createUser: async ({}, { user }, ctx) => {
            await ctx.table(User).create(user);

            return true;
        },
        deleteUser: async ({}, { user }, ctx) => {
            await ctx.table(User).destroy({
                where: {
                    username: user,
                },
            });

            return true;
        },
        createProblem: async ({}, { problem }, ctx) => {
            await ctx.table(Problem).create(problem);

            return true;
        },
        updateProblem: async ({}, { problem }, ctx) => true, // TODO
        deleteProblem: async ({}, { problem }, ctx) => {
            await ctx.table(Problem).destroy({
                where: {
                    name: problem,
                },
            });
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
        },
        ...contestMutationResolvers,
    },
};
