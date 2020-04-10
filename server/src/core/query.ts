import { gql } from 'apollo-server-core';
import { ModelRoot } from '../main/model-root';
import { Resolvers } from '../main/resolver-types';
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
        fileCollection(uuid: ID!): FileCollection!
    }
`;

export interface QueryModelRecord {
    Query: ModelRoot;
}

export interface QueryModelRecord {
    Query: ModelRoot;
}

export const queryResolvers: Resolvers = {
    Query: {
        mainView: async (root, { username }): Promise<MainView> =>
            new MainView(
                root,
                username !== null && username !== undefined
                    ? (await root.table(User).findOne({ where: { username } })) ??
                      root.fail(`no such user: ${username}`)
                    : null,
            ),
        users: async root => root.table(User).findAll({ include: [root.table(Contest)] }),
        user: async (root, { username }) =>
            (await root.table(User).findOne({ where: { username } })) ?? root.fail(`no such user: ${username}`),
        contests: async root => root.table(Contest).findAll(),
        contest: async (root, { name }) =>
            (await root.table(Contest).findOne({ where: { name } })) ?? root.fail(`no such contest: ${name}`),
        problems: async root => root.table(Problem).findAll(),
        problem: async (root, { name }) =>
            (await root.table(Problem).findOne({ where: { name } })) ?? root.fail(`no such problem: ${name}`),
        fileCollection: (_, { uuid }) => ({ uuid }),
    },
};
