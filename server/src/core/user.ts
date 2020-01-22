import { gql } from 'apollo-server-core';
import { AllowNull, AutoIncrement, Column, HasMany, Index, PrimaryKey, Table, Unique } from 'sequelize-typescript';
import { BaseModel } from '../main/base-model';
import { ResolversWithModels } from '../main/resolver-types';
import { Participation } from './participation';

export const userSchema = gql`
    type User {
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
export class User extends BaseModel<User> {
    @PrimaryKey
    @AutoIncrement
    @Column
    id!: number;

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

    /** Contest wich the user belongs to */
    @HasMany(() => Participation)
    partitipations!: Participation[];
}

/** Privilege of a user */
export enum UserRole {
    /** Normal user, can take part in a contest */
    USER,
    /** Admin user, can do everything */
    ADMIN,
}

export const userResolvers: ResolversWithModels<{
    User: User;
}> = {
    User: {
        username: user => user.username,
        name: user => user.name,
    },
};
