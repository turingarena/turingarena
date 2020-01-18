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
        getFile(hash: ID!): File!
    }
`;

export const queryResolvers: Resolvers = {
    Query: {
        users: async ({}, {}, ctx) =>
            ctx.db.User.findAll({ include: [ctx.db.Contest] }),
        user: async ({}, { username }, ctx) =>
            ctx.db.User.findOne({
                where: { username },
                include: [ctx.db.Contest],
            }),
        contests: async ({}, {}, ctx) =>
            ctx.db.Contest.findAll({ include: [ctx.db.User, ctx.db.Problem] }),
        contest: async ({}, { name }, ctx) =>
            ctx.db.Contest.findOne({
                where: { name },
                include: [ctx.db.User, ctx.db.Problem],
            }),
        problems: async ({}, {}, ctx) =>
            ctx.db.Problem.findAll({ include: [ctx.db.Contest] }),
        problem: async ({}, { name }, ctx) =>
            ctx.db.Problem.findOne({
                where: { name },
                include: [ctx.db.Contest],
            }),
    },
};
