import { gql } from 'apollo-server-core';
import { AllowNull, Column, Index, Table, Unique } from 'sequelize-typescript';
import { ApiObject } from '../main/api';
import { createSimpleLoader, UuidBaseModel } from '../main/base-model';
import { Resolvers } from '../main/resolver-types';

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

/** A user in TuringArena */
@Table
export class User extends UuidBaseModel<User> {
    /** Username that is used to identify the user, e.g. alerighi */
    @Unique
    @Index
    @AllowNull(false)
    @Column
    username!: string;

    /** Full name of the user, e.g. Mario Rossi */
    @AllowNull(false)
    @Column
    name!: string;

    /** Login token of the user, must be unique for each user, e.g. fjdkah786 */
    @Unique
    @Index
    @AllowNull(false)
    @Column
    token!: string;

    /** Privilege of the user */
    @AllowNull(false)
    @Column
    role!: UserRole;
}

/** Privilege of a user */
export enum UserRole {
    /** Normal user, can take part in a contest */
    USER,
    /** Admin user, can do everything */
    ADMIN,
}

export interface UserModelRecord {
    User: User;
}

export class UserApi extends ApiObject {
    byUsername = createSimpleLoader((username: string) => this.ctx.table(User).findOne({ where: { username } }));
    byToken = createSimpleLoader((token: string) => this.ctx.table(User).findOne({ where: { token } }));
}

export const userResolvers: Resolvers = {
    User: {
        id: u => u.id,
        username: u => u.username,
        name: u => u.name,
    },
};
