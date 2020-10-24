import { gql } from 'apollo-server-core';
import { ApiObject } from '../main/api';
import { createSimpleLoader } from '../main/base-model';
import { Resolvers } from '../main/resolver-types';
import { typed } from '../util/types';
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

export interface User {
    __typename: 'User';
    contest: Contest;
    username: string;
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

        return typed<User>({ __typename: 'User', contest, username });
    }
}

export interface UserModelRecord {
    User: User;
}

export const userResolvers: Resolvers = {
    User: {
        id: ({ contest, username }) => `${contest.id}/${username}`,
        username: u => u.username,
        name: async (u, {}, ctx) => (await ctx.api(UserApi).metadataLoader.load(u)).name,
    },
};
