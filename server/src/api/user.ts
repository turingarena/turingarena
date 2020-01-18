import { gql } from 'apollo-server-core';
import { Resolvers } from '../generated/graphql-types';

export const userSchema = gql`
    type User {
        username: ID!
        name: String!
    }

    input UserInput {
        username: ID!
        name: String!
        token: String!
        isAdmin: Boolean!
    }
`;

export const userResolvers: Resolvers = {
    User: {
        username: user => user.username,
        name: user => user.name,
    },
};
