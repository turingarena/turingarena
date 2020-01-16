import { gql } from 'apollo-server-core';
import { Column, Model, PrimaryKey, Table } from 'sequelize-typescript';
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

@Table
export class User extends Model<User> {
    @Column({ primaryKey: true, autoIncrement: true })
    id!: number;

    @Column({ unique: true })
    username!: string;

    @Column
    name!: string;

    @Column
    token!: string;

    @Column
    isAdmin!: boolean;
}

export const userResolvers: Resolvers = {
    User: {
        username: (user) => user.username,
        name: (user) => user.name,
    },
};
