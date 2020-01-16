import { gql } from 'apollo-server-core';
import { Resolvers } from '../generated/graphql-types';

export const querySchema = gql`
    type Query {
        users: [User!]!
        user(username: ID!): User!
    }
`;

export const queryResolvers: Resolvers = {
    Query: {
        users: async ({}, {}, ctx) => ctx.db.User.findAll(),
        user: async({}, {username}, ctx) => ctx.db.User.findOne({ where: { username }}),
        // value: async () => 'a string',
    },
};
