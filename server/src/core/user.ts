import { gql } from 'apollo-server-core';
import { Resolvers } from '../main/resolver-types';
import { UserMetadata } from './contest-metadata';

export const userSchema = gql`
    type User {
        id: ID!

        username: ID!
        name: String!
    }

    input UserInput {
        username: ID!
        name: String!
        token: String!
        role: UserRole!
    }

    enum UserRole {
        USER
        ADMIN
    }
`;

export class User {
    constructor(readonly contestId: string, readonly metadata: UserMetadata) {}
}

export interface UserModelRecord {
    User: User;
}

export const userResolvers: Resolvers = {
    User: {
        id: u => `${u.contestId}/${u.metadata.username}`,
        username: u => u.metadata.username,
        name: u => u.metadata.name,
    },
};
