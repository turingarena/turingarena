import { gql } from 'apollo-server-core';
import { Resolvers } from '../generated/graphql-types';

export const querySchema = gql`
    type Query {
        users: [User!]!
        user(username: ID!): User!
        contests: [Contest!]!
        contest(name: ID!): Contest!
    }
`;

export const queryResolvers: Resolvers = {
    Query: {
        users: async ({}, {}, ctx) => ctx.db.User.findAll(),
        user: async ({}, {username}, ctx) => ctx.db.User.findOne({ where: { username }}),
        contests: async ({}, {}, ctx) => ctx.db.Contest.findAll(),
        contest: async ({}, {name}, ctx) => ctx.db.Contest.findOne({ where: { name }}),
        // value: async () => 'a string',
    },
};
