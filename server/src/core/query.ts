import { gql } from 'apollo-server-core';
import { Resolvers } from '../generated/graphql-types';

export const querySchema = gql`
    type Query {
        users: [User!]!
        user(username: ID!): User!
        contests: [Contest!]!
        contest(name: ID!): Contest!
        problems: [Problem!]!
        problem(name: ID!): Problem!
        fileContent(hash: ID!): FileContent!
    }
`;

export const queryResolvers: Resolvers = {
    Query: {
        users: async ({}, {}, ctx) => ctx.db.User.findAll({ include: [ctx.db.Contest] }),
        user: async ({}, { username }, ctx) =>
            (await ctx.db.User.findOne({ where: { username } })) ?? ctx.fail(`no such user: ${username}`),
        contests: async ({}, {}, ctx) => ctx.db.Contest.findAll(),
        contest: async ({}, { name }, ctx) =>
            (await ctx.db.Contest.findOne({ where: { name } })) ?? ctx.fail(`no such contest: ${name}`),
        problems: async ({}, {}, ctx) => ctx.db.Problem.findAll(),
        problem: async ({}, { name }, ctx) =>
            (await ctx.db.Problem.findOne({ where: { name } })) ?? ctx.fail(`no such problem: ${name}`),
    },
};
