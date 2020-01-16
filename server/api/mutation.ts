import { gql } from 'apollo-server-core';
import { Resolvers, UserInput } from '../generated/graphql-types';

export const mutationSchema = gql`
    type Mutation {
        init: Boolean!
        contest(name: ID!): ContestMutations!
        createUser(user: UserInput!): Boolean!
        updateUser(user: UserInput!): Boolean!
        deleteUser(user: ID!): Boolean!
        createProblem(problem: ProblemInput!): Boolean!
        deleteProblem(problem: ID!): Boolean!
        updateProblem(problem: ProblemInput!): Boolean!
        createContest(contest: ContestInput!): Boolean!
        updateContest(contest: ContestInput!): Boolean!
        deleteContest(contest: ID!): Boolean!
    }
`;

export const mutationResolvers: Resolvers = {
    Mutation: {
        init: async ({}, {}, ctx) => {
            await ctx.sequelize.sync();

            return true;
        },
        updateUser: async ({}, {user}, ctx) => {
            // TODO
            return true;
        },
        createUser: async ({}, {user}, ctx) => {
            await ctx.db.User.create(user);

            return true;
        },
        deleteUser: async ({}, {user}, ctx) => {
            await ctx.db.User.destroy({
                where: {
                    username: user,
                } });

            return true;
        },
        createProblem: async ({}, {problem}, ctx) => {
            await ctx.db.Problem.create(problem);

            return true;
        },
        updateProblem: async ({}, {problem}, ctx) => {
            // TODO

            return true;
        },
        deleteProblem: async ({}, {problem}, ctx) => {
            await ctx.db.Problem.destroy({
                where: {
                    name: problem,
                }});
        },
        createContest: async ({}, {contest}, ctx) => {
            await ctx.db.Contest.create(contest);

            return true;
        },
        updateContest: async ({}, {contest}, ctx) => {
            // TODO

            return true;
        },
        deleteContest: async ({}, {contest}, ctx) => {
            await ctx.db.Contest.destroy({
                                             where: {
                                                 name,
                                             }})
        },
        contest: async ({}, {name}, ctx) => {
            const contest = await ctx.db.Contest.findOne({where:{name}});

            return {contest};
        },
    },
};
