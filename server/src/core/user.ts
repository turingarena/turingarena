import { gql } from 'apollo-server-core';
import { ApiCache } from '../main/api-cache';
import { ApiContext } from '../main/api-context';
import { createSimpleLoader } from '../main/base-model';
import { ApiOutputValue } from '../main/graphql-types';
import { unreachable } from '../util/unreachable';
import { Contest } from './contest';
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
    }
`;

export class User implements ApiOutputValue<'User'> {
    constructor(readonly contest: Contest, readonly metadata: UserMetadata, readonly ctx: ApiContext) {}
    __typename = 'User' as const;

    username = this.metadata.username;

    id = `${this.contest.id}/${this.username}`;

    async name() {
        return (await this.ctx.cache(UserCache).byId.load(this.id)).name;
    }

    static async fromId(id: string, ctx: ApiContext) {
        const [contestId, username] = id.split('/');
        const contest = new Contest(contestId, ctx);
        return contest.getUserByName(username);
    }
}

export class UserCache extends ApiCache {
    byId = createSimpleLoader(async (id: string) => {
        const user = await User.fromId(id, this.ctx);
        const contestMetadata = await user.contest.getMetadata();

        return (
            contestMetadata.users.find(data => data.username === user.username) ??
            unreachable(`user ${user.username} does not exist in contest ${user.contest.id}`)
        );
    });
}
