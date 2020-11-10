import { gql } from 'apollo-server-core';
import { ApiObject } from '../main/api';
import { ApiContext } from '../main/api-context';
import { createSimpleLoader } from '../main/base-model';
import { Contest, ContestApi } from './contest';

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
        return (await ctx.api(UserApi).metadataLoader.load(this)).name;
    }
}

export class UserApi extends ApiObject {
    metadataLoader = createSimpleLoader(async ({ contest, username }: User) => {
        const contestMetadata = await this.ctx.api(ContestApi).getMetadata(contest);

        return (
            contestMetadata.users.find(data => data.username === username) ??
            this.ctx.fail(`user ${username} does not exist in contest ${contest.id}`)
        );
    });

    async validate(user: User) {
        await this.metadataLoader.load(user);

        return user;
    }

    async getUserByToken(contest: Contest, token: string) {
        const contestMetadata = await this.ctx.api(ContestApi).getMetadata(contest);
        const userMetadata = contestMetadata.users.find(data => data.token === token) ?? null;

        if (userMetadata === null) return null;
        const { username } = userMetadata;

        return new User(contest, username);
    }
}

export interface UserModelRecord {
    User: User;
}
