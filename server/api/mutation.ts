import { gql } from 'apollo-server-core';
import { Resolvers, UserInput } from '../generated/graphql-types';

export const mutationSchema = gql`
    type Mutation {
        init: Query
        createUser(user: UserInput!): Query
        updateUser(user: UserInput!): Query
        removeUser(user: ID!): Query
        #createPrblem(problem: ProblemInput!): Query
        #removeProblem(problem: ID!): Query
        #updateProblem(problem: ProblemInput!): Query
        #createContest(contest: ContestInput!): Query
        #updateContest(contest: ContestInput!): Query
        #removeContest(contest: ID!): Query
    }
`;

export const mutationResolvers: Resolvers = {
    Mutation: {
        init: async ({}, {}, ctx) => {
            await ctx.sequelize.sync();

            return {};
        },
        createUser: async (a, {user}, ctx) => {
            await ctx.db.User.create(user);

            return {};
        },
        removeUser: async ({}, {user}, ctx) => {
            await ctx.db.User.destroy({
                where: {
                    username: user,
                } });

            return {};
        },
    },
};
