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
        return (await ctx.api(UserCache).metadataLoader.load(this.id())).name;
    }

    async validate(ctx: ApiContext) {
        await ctx.api(UserCache).metadataLoader.load(this.id());

        return this;
    }

    static fromId(id: string, ctx: ApiContext): User {
        const [contestId, username] = id.split('/');

        return new User(new Contest(contestId, ctx), username);
    }
}

export class UserCache extends ApiObject {
    metadataLoader = createSimpleLoader(async (id: string) => {
        const user = User.fromId(id, this.ctx);
        const contestMetadata = await user.contest.getMetadata();

        return (
            contestMetadata.users.find(data => data.username === user.username) ??
            this.ctx.fail(`user ${user.username} does not exist in contest ${user.contest.id}`)
        );
    });
}

export interface UserModelRecord {
    User: User;
}
