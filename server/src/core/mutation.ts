import { gql } from 'apollo-server-core';
import { Resolvers } from '../main/resolver-types';
import { Contest, ContestApi } from './contest';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { Participation } from './participation';
import { Problem, ProblemApi } from './problem';
import { SubmitApi } from './submit';
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

        submit(submission: SubmissionInput!): Submission!

        logIn(token: String!): AuthResult
    }
`;

export interface MutationModelRecord {
    Mutation: {};
}

export const mutationResolvers: Resolvers = {
    Mutation: {
        init: async ({}, {}, ctx) => {
            await ctx.environment.sequelize.sync();

            return true;
        },
        updateUser: async ({}, { user }, ctx) => true, // TODO
        createUser: async ({}, { user }, ctx) => {
            await ctx.table(User).create(user);

            return true;
        },
        deleteUser: async ({}, { user }, ctx) => {
            await ctx.table(User).destroy({
                where: {
                    username: user,
                },
            });

            return true;
        },
        createProblem: async ({}, { problem }, ctx) => {
            await ctx.table(Problem).create(problem);

            return true;
        },
        updateProblem: async ({}, { problem }, ctx) => true, // TODO
        deleteProblem: async ({}, { problem }, ctx) => {
            await ctx.table(Problem).destroy({
                where: {
                    name: problem,
                },
            });

            return true;
        },
        createContest: async ({}, { contest }, ctx) => {
            await ctx.table(Contest).create(contest);

            return true;
        },
        updateContest: async ({}, { contest }, ctx) => true, // TODO
        deleteContest: async ({}, { contest }, ctx) => {
            await ctx.table(Contest).destroy({
                where: {
                    name,
                },
            });

            return true;
        },
        submit: ({}, { submission }, ctx) => ctx.api(SubmitApi).submit(submission),
        logIn: ({}, { token }, ctx) => ctx.environment.authService.logIn(token),

        addProblem: async ({}, { contestName, name }, ctx) => {
            const contest = await ctx.api(ContestApi).byName.load(contestName);
            const problem = await ctx.api(ProblemApi).byName.load(name);
            await ctx.table(ContestProblemAssignment).create({
                contestId: contest.id,
                problemId: problem.id,
            });

            return true;
        },
        addUser: async ({}, { contestName, username }, ctx) => {
            const contest = await ctx.api(ContestApi).byName.load(contestName);
            const user = await ctx.api(UserApi).byUsername.load(username);
            await ctx.table(Participation).create({ userId: user.id, contestId: contest.id });

            return true;
        },
    },
};
