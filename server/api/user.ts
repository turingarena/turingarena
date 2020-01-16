import { gql } from 'apollo-server-core';
import {
    AutoIncrement,
    BelongsToMany,
    Column,
    HasMany,
    Index,
    Model,
    PrimaryKey,
    Table,
    Unique
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
    @PrimaryKey
    @AutoIncrement
    @Column
    id!: number;

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
    isAdmin!: boolean;

    @BelongsToMany(() => Contest, () => Participation)
    contests!: Contest[];
}

export const userResolvers: Resolvers = {
    User: {
        username: (user) => user.username,
        name: (user) => user.name,
    },
};
