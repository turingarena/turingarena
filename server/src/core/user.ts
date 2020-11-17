import { gql } from 'apollo-server-core';
import { ApiObject } from '../main/api';
import { ApiContext } from '../main/api-context';
import { createSimpleLoader } from '../main/base-model';
import { Contest } from './contest';

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

export enum UserRole {
    USER,
    ADMIN,
}

export class User {
    constructor(readonly contest: Contest, readonly username: string) {}
    __typename = 'User';
    id() {
        return `${this.contest.id}/${this.username}`;
    }
    async name({}, ctx: ApiContext) {
        return (await ctx.api(UserCache).metadataLoader.load(this)).name;
    }

    async validate(ctx: ApiContext) {
        await ctx.api(UserCache).metadataLoader.load(this);

        return this;
    }
}

export class UserCache extends ApiObject {
    metadataLoader = createSimpleLoader(async ({ contest, username }: User) => {
        const contestMetadata = await contest.getMetadata(this.ctx);

        return (
            contestMetadata.users.find(data => data.username === username) ??
            this.ctx.fail(`user ${username} does not exist in contest ${contest.id}`)
        );
    });
}

export interface UserModelRecord {
    User: User;
}
