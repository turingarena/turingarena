import { gql } from 'apollo-server-core';
import { Resolvers } from '../generated/graphql-types';
import { Contest } from './contest';
import { MainView } from './main-view';
import { Problem } from './problem';
import { User } from './user';

export const querySchema = gql`
    type Query {
        mainView(username: ID): MainView!

        users: [User!]!
        user(username: ID!): User!
        contests: [Contest!]!
        contest(name: ID!): Contest!
        problems: [Problem!]!
        problem(name: ID!): Problem!
        fileContent(hash: ID!): FileContent!
    }
`;

export const queryResolvers: Resolvers = {
    Query: {
        mainView: async ({}, { username }, ctx): Promise<MainView> => ({
            user:
                username !== null && username !== undefined
                    ? (await ctx.table(User).findOne({ where: { username } })) ?? ctx.fail(`no such user: ${username}`)
                    : null,
        }),
        users: async ({}, {}, ctx) => ctx.table(User).findAll({ include: [ctx.table(Contest)] }),
        user: async ({}, { username }, ctx) =>
            (await ctx.table(User).findOne({ where: { username } })) ?? ctx.fail(`no such user: ${username}`),
        contests: async ({}, {}, ctx) => ctx.table(Contest).findAll(),
        contest: async ({}, { name }, ctx) =>
            (await ctx.table(Contest).findOne({ where: { name } })) ?? ctx.fail(`no such contest: ${name}`),
        problems: async ({}, {}, ctx) => ctx.table(Problem).findAll(),
        problem: async ({}, { name }, ctx) =>
            (await ctx.table(Problem).findOne({ where: { name } })) ?? ctx.fail(`no such problem: ${name}`),
    },
};
