import { gql } from 'apollo-server-core';
import { ApiCache } from '../main/api-cache';
import { ApiContext } from '../main/api-context';
import { createSimpleLoader } from '../main/base-model';
import { unreachable } from '../util/unreachable';
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
    }
`;

export class User {
    constructor(readonly contest: Contest, readonly username: string, readonly ctx: ApiContext) {}
    __typename = 'User' as const;

    id = `${this.contest.id}/${this.username}`;

    async name() {
        return (await this.ctx.cache(UserCache).byId.load(this.id)).name;
    }

    async validate() {
        await this.ctx.cache(UserCache).byId.load(this.id);

        return this;
    }

    static fromId(id: string, ctx: ApiContext): User {
        const [contestId, username] = id.split('/');

        return new User(new Contest(contestId, ctx), username, ctx);
    }
}

export class UserCache extends ApiCache {
    byId = createSimpleLoader(async (id: string) => {
        const user = User.fromId(id, this.ctx);
        const contestMetadata = await user.contest.getMetadata();

        return (
            contestMetadata.users.find(data => data.username === user.username) ??
            unreachable(`user ${user.username} does not exist in contest ${user.contest.id}`)
        );
    });
}
