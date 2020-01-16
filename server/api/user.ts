import { gql } from 'apollo-server-core';
import {
    BelongsToMany,
    Column,
    Index,
    Model,
    Table,
    Unique,
} from 'sequelize-typescript';
import { Resolvers } from '../generated/graphql-types';
import { Contest, Participation } from './contest';

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

@Table
export class User extends Model<User> {
    @Unique
    @Index
    @Column
    username!: string;

    @Column
    name!: string;

    @Unique
    @Index
    @Column
    token!: string;

    @Column
    privilege!: UserPrivilege;

    @BelongsToMany(() => Contest, () => Participation)
    contests!: Contest[];
}

export enum UserPrivilege {
    USER,
    ADMIN,
}

export const userResolvers: Resolvers = {
    User: {
        username: (user) => user.username,
        name: (user) => user.name,
    },
};
