import { gql } from 'apollo-server-core';
import { ModelRoot } from '../main/model-root';
import { Resolvers } from '../main/resolver-types';
import { Contest, ContestApi } from './contest';
import { MainView } from './main-view';
import { Problem, ProblemApi } from './problem';
import { Submission } from './submission';
import { User, UserApi } from './user';

export const querySchema = gql`
    type Query {
        mainView(username: ID): MainView!

        users: [User!]!
        user(username: ID!): User!
        contests: [Contest!]!
        contest(name: ID!): Contest!
        problems: [Problem!]!
        problem(name: ID!): Problem!
        fileContent(id: ID!): FileContent!
        fileCollection(uuid: ID!): FileCollection!
        submission(id: ID!): Submission!
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
        mainView: async (root, { username }, ctx): Promise<MainView> =>
            new MainView(
                root,
                username !== null && username !== undefined ? await ctx.api(UserApi).byUsername.load(username) : null,
            ),
        users: async root => root.table(User).findAll({ include: [root.table(Contest)] }),
        user: async (root, { username }, ctx) => ctx.api(UserApi).byUsername.load(username),
        contests: async root => root.table(Contest).findAll(),
        contest: async (root, { name }, ctx) => ctx.api(ContestApi).byName.load(name),
        problems: async root => root.table(Problem).findAll(),
        problem: async (root, { name }, ctx) => ctx.api(ProblemApi).byName.load(name),
        fileCollection: (_, { uuid }) => ({ uuid }),
        submission: async (root, { id }) =>
            // TODO: check authorization
            (await root.table(Submission).findByPk(id)) ?? root.fail(`no such submission: ${id}`),
        fileContent: async root => root.fail(`not implemented`),
    },
};
