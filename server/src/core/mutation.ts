import { gql } from 'apollo-server-core';
import { ModelRoot } from '../main/model-root';
import { Resolvers } from '../main/resolver-types';
import { Contest, ContestApi } from './contest';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { Participation } from './participation';
import { Problem } from './problem';
import { submit } from './submit';
import { User, UserApi } from './user';

export const mutationSchema = gql`
    type Mutation {
        init: Boolean!

        createUser(user: UserInput!): Boolean!
        updateUser(user: UserInput!): Boolean!
        deleteUser(user: ID!): Boolean!
        createProblem(problem: ProblemInput!): Boolean!
        deleteProblem(problem: ID!): Boolean!
        updateProblem(problem: ProblemInput!): Boolean!
        createContest(contest: ContestInput!): Boolean!
        updateContest(contest: ContestInput!): Boolean!
        deleteContest(contest: ID!): Boolean!

        # createFile(file: FileContentInput!): Boolean!
        # deleteFile(id: ID!): Boolean!

        addProblem(contestName: ID!, name: ID!): Boolean!
        # removeProblem(contestName: ID!, name: ID!): Boolean!

        addUser(contestName: ID!, username: ID!): Boolean!
        # removeUser(contestName: ID!, username: ID!): Boolean!

        submit(submission: SubmissionInput!): Boolean!

        logIn(token: String!): AuthResult
    }
`;

export interface MutationModelRecord {
    Mutation: ModelRoot;
}

export const mutationResolvers: Resolvers = {
    Mutation: {
        init: async root => {
            await root.sequelize.sync();

            return true;
        },
        updateUser: async (root, { user }) => true, // TODO
        createUser: async (root, { user }) => {
            await root.table(User).create(user);

            return true;
        },
        deleteUser: async (root, { user }) => {
            await root.table(User).destroy({
                where: {
                    username: user,
                },
            });

            return true;
        },
        createProblem: async (root, { problem }) => {
            await root.table(Problem).create(problem);

            return true;
        },
        updateProblem: async (root, { problem }) => true, // TODO
        deleteProblem: async (root, { problem }) => {
            await root.table(Problem).destroy({
                where: {
                    name: problem,
                },
            });

            return true;
        },
        createContest: async (root, { contest }) => {
            await root.table(Contest).create(contest);

            return true;
        },
        updateContest: async (root, { contest }) => true, // TODO
        deleteContest: async (root, { contest }) => {
            await root.table(Contest).destroy({
                where: {
                    name,
                },
            });

            return true;
        },
        submit: (root, { submission }) => submit(root, submission).then(() => true),
        logIn: (root, { token }) => root.authService.logIn(token),

        addProblem: async (root, { contestName, name }, ctx) => {
            const contest = await ctx.api(ContestApi).byName.load(contestName);
            const problem =
                (await root.table(Problem).findOne({ where: { name } })) ?? root.fail(`no such problem '${name}'`);
            await root.table(ContestProblemAssignment).create({
                contestId: contest.id,
                problemId: problem.id,
            });

            return true;
        },
        addUser: async (root, { contestName, username }, ctx) => {
            const contest = await ctx.api(ContestApi).byName.load(contestName);
            const user = await ctx.api(UserApi).byUsername.load(username);
            await root.table(Participation).create({ userId: user.id, contestId: contest.id });

            return true;
        },
    },
};
